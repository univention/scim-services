#
# SPDX-FileCopyrightText: 2023 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

import inspect
import itertools
from pathlib import Path

import pytest
import univention.scim.server
from pytestarch import EvaluableArchitecture, LayerRule, LayeredArchitecture, Rule, get_evaluable_architecture


@pytest.fixture(scope="session")
def architecture() -> LayeredArchitecture:
    return (
        LayeredArchitecture()
        .layer("authn")
        .containing_modules(["univention.scim.server.authn"])
        .layer("authz")
        .containing_modules(["univention.scim.server.authz"])
        .layer("domain")
        .containing_modules(["univention.scim.server.domain"])  # have_modules_with_names_matching() doesn't work for me
        .layer("model_service")  # or we could split "repo", "repo.udm", and "rules" from "domain".
        .containing_modules(["univention.scim.server.model_service"])
        .layer("rest")
        .containing_modules(["univention.scim.server.main", "univention.scim.server.rest"])
    )


@pytest.fixture(scope="session")
def base_path() -> Path:
    """
    Will return the absolute path for .../scim-services/scim-server/src/univention ,
    so we can use full Python paths: "univention.scim.server...."
    """
    return Path(inspect.getsourcefile(univention.scim.server)).parent.parent.parent  # type: ignore


@pytest.fixture(scope="session")
def evaluable(base_path: Path) -> EvaluableArchitecture:
    assert str(base_path).endswith("univention")
    return get_evaluable_architecture(str(base_path), str(base_path))


@pytest.mark.parametrize(
    ["importer", "imported"],
    [
        ("domain", "model_service"),
        ("rest", "authn"),
        # TODO: ("rest", "authz"),  # not implemented
        ("rest", "domain"),
    ],
)
def test_layer_should(
    architecture: LayeredArchitecture, evaluable: EvaluableArchitecture, importer: str, imported: str
) -> None:
    rule = (
        LayerRule()
        .based_on(architecture)
        .layers_that()
        .are_named(importer)
        .should()
        .access_layers_that()
        .are_named(imported)
    )
    rule.assert_applies(evaluable)


@pytest.mark.parametrize(
    ["importer", "imported"],
    list(itertools.product(["authn"], ["authz", "domain", "rest"]))
    + list(itertools.product(["authz"], ["authn", "domain", "model_service", "rest"]))
    + list(itertools.product(["domain"], ["authn", "authz", "rest"]))
    + list(itertools.product(["model_service"], ["authn", "authz", "domain", "rest"])),
)
def test_layer_should_not(
    architecture: LayeredArchitecture, evaluable: EvaluableArchitecture, importer: str, imported: str
) -> None:
    rule = (
        LayerRule()
        .based_on(architecture)
        .layers_that()
        .are_named(importer)
        .should_not()
        .access_layers_that()
        .are_named(imported)
    )
    rule.assert_applies(evaluable)


@pytest.mark.parametrize(
    ["importer", "imported"],
    itertools.permutations(
        ["univention.scim.server.authn", "univention.scim.server.authz", "univention.scim.server.domain.repo.udm"],
        2,
    ),
)
def test_adapters_dont_import_adapters(evaluable: EvaluableArchitecture, importer: str, imported: str) -> None:
    rule = (
        Rule()
        .modules_that()
        .are_sub_modules_of(imported)
        .should_not()
        .be_imported_by_modules_that()
        .are_sub_modules_of(importer)
    )
    rule.assert_applies(evaluable)


def test_business_only_imports_business(evaluable: EvaluableArchitecture) -> None:
    rule = (
        Rule()
        .modules_that()
        .have_name_matching(r"^univention\.scim\.server\.domain\.(crud_scim|group_*|user_*|repo.crud_*|rules\..*)")
        .should_not()
        .import_modules_that()
        .have_name_matching(r"^univention\.scim\.server\.(authn|authz|domain\.repo\.udm|model_service|rest)")
    )
    rule.assert_applies(evaluable)
