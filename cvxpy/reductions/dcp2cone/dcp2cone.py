"""
Copyright 2013 Steven Diamond, 2017 Akshay Agrawal, 2017 Robin Verschueren

This file is part of CVXPY.

CVXPY is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY.  If not, see <http://www.gnu.org/licenses/>.
"""

from cvxpy.reductions.dcp2cone.atom_canonicalizers import CANON_METHODS as cone_canon_methods
from cvxpy.reductions.canonicalization import Canonicalization
from cvxpy.problems.problem import Problem
from cvxpy.problems.attributes import (is_dcp, is_minimization, is_constrained,
                                       has_pwl_atoms, has_soc_atoms, has_exp_atoms, has_psd_atoms)
from cvxpy.constraints.constraint import Constraint
from cvxpy.expressions.attributes import is_affine
from cvxpy.problems.objective import Minimize
from cvxpy.constraints.attributes import (exists, is_cone_constraint, are_arguments_affine)
from cvxpy.constraints import (Zero, NonPos, SOC, PSD, ExpCone)


class Dcp2Cone(Canonicalization):

    preconditions = {
        (Problem, is_dcp, True),
        (Problem, is_minimization, True),
        (Constraint, is_cone_constraint, True)
    }

    @staticmethod
    def postconditions(problem_type):
        post = {
            (Problem, is_dcp, True),
            (Problem, is_minimization, True),
            (Minimize, is_affine, True),
            (Constraint, are_arguments_affine, True),
            (Constraint, is_cone_constraint, True),
            (Zero, exists, True)  # Probably have equality constraints.
        }
        # Atoms generate cone constraints.
        for cond_func, cone in [(has_pwl_atoms, NonPos),
                                (has_soc_atoms, SOC),
                                (has_exp_atoms, ExpCone),
                                (has_psd_atoms, PSD)]:
            cond = (Problem, cond_func, True)
            if cond in problem_type:
                post.add((cone, exists, True))
        return post

    def apply(self, problem):
        if not self.accepts(problem):
            raise ValueError("Cannot reduce problem to cone program")
        return Canonicalization(cone_canon_methods).apply(problem)