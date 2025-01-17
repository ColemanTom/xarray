# For reference, here is a copy of the scikit-learn copyright notice:

# BSD 3-Clause License

# Copyright (c) 2007-2021 The scikit-learn developers.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE


import inspect
import warnings
from functools import wraps

POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
EMPTY = inspect.Parameter.empty


def _deprecate_positional_args(version):
    """Decorator for methods that issues warnings for positional arguments

    Using the keyword-only argument syntax in pep 3102, arguments after the
    ``*`` will issue a warning when passed as a positional argument.

    Parameters
    ----------
    version : str
        version of the library when the positional arguments were deprecated

    Examples
    --------
    Deprecate passing `b` as positional argument:

    def func(a, b=1):
        pass

    @_deprecate_positional_args("v0.1.0")
    def func(a, *, b=2):
        pass

    func(1, 2)

    Notes
    -----
    This function is adapted from scikit-learn under the terms of its license. See
    licences/SCIKIT_LEARN_LICENSE
    """

    def _decorator(f):

        signature = inspect.signature(f)

        pos_or_kw_args = []
        kwonly_args = []
        for name, param in signature.parameters.items():
            if param.kind == POSITIONAL_OR_KEYWORD:
                pos_or_kw_args.append(name)
            elif param.kind == KEYWORD_ONLY:
                kwonly_args.append(name)
                if param.default is EMPTY:
                    # IMHO `def f(a, *, b):` does not make sense -> disallow it
                    # if removing this constraint -> need to add these to kwargs as well
                    raise TypeError("Keyword-only param without default disallowed.")
            elif param.kind == POSITIONAL_ONLY:
                raise TypeError("Cannot handle positional-only params")
                # because all args are coverted to kwargs below

        @wraps(f)
        def inner(*args, **kwargs):
            n_extra_args = len(args) - len(pos_or_kw_args)
            if n_extra_args > 0:

                extra_args = ", ".join(kwonly_args[:n_extra_args])

                warnings.warn(
                    f"Passing '{extra_args}' as positional argument(s) "
                    f"was deprecated in version {version} and will raise an error two "
                    "releases later. Please pass them as keyword arguments."
                    "",
                    FutureWarning,
                )

            kwargs.update({name: arg for name, arg in zip(pos_or_kw_args, args)})

            return f(**kwargs)

        return inner

    return _decorator
