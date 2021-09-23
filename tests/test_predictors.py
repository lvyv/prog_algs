# Copyright © 2021 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.
import unittest

from prog_models import PrognosticsModel

class MockProgModel(PrognosticsModel):
    states = ['a', 'b', 'c', 't']
    inputs = ['i1', 'i2']
    outputs = ['o1']
    events = ['e1', 'e2']
    default_parameters = {
        'p1': 1.2,
    }

    def initialize(self, u = {}, z = {}):
        return {'a': 1, 'b': 5, 'c': -3.2, 't': 0}

    def next_state(self, x, u, dt):
        x['a']+= u['i1']*dt
        x['c']-= u['i2']
        x['t']+= dt
        return x

    def output(self, x):
        return {'o1': x['a'] + x['b'] + x['c']}
    
    def event_state(self, x):
        t = x['t']
        return {
            'e1': max(1-t/5.0,0),
            'e2': max(1-t/15.0,0)
            }

    def threshold_met(self, x):
        return {key : value < 1e-6 for (key, value) in self.event_state(x).items()}

class TestPredictors(unittest.TestCase):
    def test_pred_template(self):
        from predictor_template import TemplatePredictor
        m = MockProgModel()
        pred = TemplatePredictor(m)

    def test_MC(self):
        from prog_algs.predictors import MonteCarlo
        m = MockProgModel()
        mc = MonteCarlo(m)
        samples = [
            {'a': 1, 'b': 2, 'c': -3.2},
            {'a': 2, 'b': 2, 'c': -3.2},
            {'a': 0, 'b': 2, 'c': -3.2},
            {'a': 1, 'b': 1, 'c': -3.2},
            {'a': 1, 'b': 3, 'c': -3.2},
            {'a': 1, 'b': 2, 'c': -2.2},
            {'a': 1, 'b': 2, 'c': -4.2}
        ]
        def future_loading(t, x={}):
            if (t < 5):
                return {'i1': 2, 'i2': 1}
            else:
                return {'i1': -4, 'i2': 2.5}

    def test_prediction(self):
        from prog_algs.predictors.prediction import Prediction
        from prog_algs.uncertain_data import UnweightedSamples
        times = [list(range(10))]*3
        states = [list(range(10)), list(range(1, 11)), list(range(-1, 9))]
        p = Prediction(times, states)

        self.assertEqual(p[0], states[0])
        self.assertEqual(p.sample(0), states[0])
        self.assertEqual(p.sample(-1), states[-1])
        self.assertEqual(p.snapshot(0), UnweightedSamples([0, 1, -1]))
        self.assertEqual(p.snapshot(-1), UnweightedSamples([9, 10, 8]))
        self.assertEqual(p.time(0), times[0])
        self.assertEqual(p.time(-1), times[-1])

        # Out of range
        try:
            tmp = p[10]
            self.fail()
        except Exception:
            pass

        try:
            tmp = p.sample(10)
            self.fail()
        except Exception:
            pass

        try:
            tmp = p.time(10)
            self.fail()
        except Exception:
            pass

        # Bad type
        try:
            tmp = p.sample('abc')
            self.fail()
        except Exception:
            pass

# This allows the module to be executed directly    
def run_tests():
    l = unittest.TestLoader()
    runner = unittest.TextTestRunner()
    print("\n\nTesting Predictor")
    result = runner.run(l.loadTestsFromTestCase(TestPredictors)).wasSuccessful()

    if not result:
        raise Exception("Failed test")

if __name__ == '__main__':
    run_tests()
