"""Read the selected #440 records and reduce the conditional variance for display."""
from math import fsum, isclose, sqrt

STUDY = 'analyses/fixed_reaction_reference/'
KIEPE_AUTHOR = r'Kiepe et al.\ '
KIEPE_CITE = 'kiepeExperimentalDeterminationPrediction2002'
WHEEL = 'c9fbf898b14d004f915f01ed77675867908dd30d77dc28544b2860e9195c80bb'
DESIGNS = ('MEA', 'DEA', 'MDEA', 'AMP_free', 'AMP_fixed')


class FixedReference:
    def __init__(self, read):
        self.read = read
        self.handoff = read(STUDY + 'manuscript-handoff.json')
        assert self.handoff['reference_pressure_pa'] == 100000
        self.quantities = self.handoff['quantities']
        self.fits = {name: self.load(name + '/' + start + '.json.gz')
                     for name, start in self.handoff['selected_starts'].items()}
        for name, start in self.handoff['selected_starts'].items():
            fit = self.fits[name]
            assert fit['start'] == start and fit['endpoint_fingerprint'] == self.quantities[name + ' selected objective']['endpoint_fingerprint'] and fit['wheel'] == WHEEL
            assert fit['replay']['cost'] == self.value(name + ' selected objective')
            assert all(r['reference']['reference_pressure_pa'] == 100000
                       for group in fit['endpoint']['reactions'].values() for r in group)

    def load(self, relative):
        return self.read(STUDY + 'results/' + relative)

    def endpoint_record(self, relative, name):
        record = self.load(relative)
        assert record['endpoint_fingerprint'] == self.fits[name]['endpoint_fingerprint'], relative
        assert record['wheel'] == WHEEL, relative
        return record

    def value(self, key):
        return self.quantities[key]['new']

    def coverage(self, name, protocol='declared'):
        record = self.endpoint_record(f'{name}/screen/selected/{protocol}/summary.json.gz', name)
        record['confirmed'] = [r['key'] for r in record['classifications'] if any(a['confirmed'] for a in r['attempts'])]
        return record

    def conditional(self, name):
        fit = self.fits[name]
        diagnostic = fit['diagnostics']
        result = diagnostic['uncertainty'].copy()
        rows = fit['replay']['rows']
        active = diagnostic['active_bounds']
        coordinates = fit['endpoint']['coordinates']
        ids = [r['identity'] for r in coordinates]
        free = result['free_coordinates']
        errors = result['conditional_standard_error']
        assert set(free) == set(ids) - set(active) == set(errors)
        # #420 identifies Kiepe and the three pure-water Kim rows as structural constants.
        excluded = [i for i, r in enumerate(rows) if
                    (name == 'MEA' and r['group'] == 'Kiepe') or
                    (name == 'MDEA' and r['identity'] in {'fit:227', 'fit:229', 'fit:249'})]
        assert len(excluded) == {'MEA': 39, 'MDEA': 3}.get(name, 0)
        # The retained MDEA derivative at those pure-water rows is roundoff at < 3e-33.
        J = diagnostic['jacobian_bound_normalized']
        assert all(max(map(abs, J[i])) < 3e-33 for i in excluded)
        all_variance = 2 * fsum(r['cost'] for r in rows) / (len(rows) - len(free))
        assert isclose(all_variance, result['residual_variance'], rel_tol=1e-12)
        responsive = len(rows) - len(excluded)
        dof = responsive - len(free)
        variance = 2 * fsum(r['cost'] for i, r in enumerate(rows) if i not in excluded) / dof
        result.update(coordinates=coordinates, active_bounds=[ids.index(k) for k in active],
                      stage_variance=variance, responsive=responsive, dof=dof,
                      conditional_standard_error={k: v * sqrt(variance / all_variance) for k, v in errors.items()})
        return result

    def mea_pressure_uncertainty(self):
        """Local parameter-only uncertainty from the fitted weighted log residuals."""
        from numpy import array, einsum, sqrt

        fit = self.fits['MEA']
        uncertainty = self.conditional('MEA')
        free = uncertainty['free_coordinates']
        coordinates = uncertainty['coordinates']
        interior = [i for i, q in enumerate(coordinates) if q['identity'] in free]
        assert [coordinates[i]['identity'] for i in interior] == free
        width = array([coordinates[i]['bounds'][1]-coordinates[i]['bounds'][0] for i in interior])
        errors = array([uncertainty['conditional_standard_error'][k] for k in free])
        covariance = array(uncertainty['conditional_correlation']) * errors[:, None] * errors[None, :]
        rows = fit['replay']['rows']
        indices = [i for i, q in enumerate(rows) if q['group'] == 'common149' and q['unit'] == 'Pa']
        assert len(indices) == 47
        jacobian = array(fit['diagnostics']['jacobian_bound_normalized'])[indices][:, interior] / width
        weight = array([rows[i]['row']['weight'] for i in indices])
        relative = sqrt(einsum('ij,jk,ik->i', jacobian, covariance, jacobian)/weight)
        return [dict(identity=rows[i]['identity'], value=rows[i]['value'], relative_SE=float(error))
                for i, error in zip(indices, relative, strict=True)]
