from typing import Iterable, Optional, Union, cast

from django.db.models import QuerySet

from baserow.core.db import specific_iterator
from baserow.core.exceptions import ApplicationOperationNotSupported
from baserow.core.integrations.exceptions import IntegrationDoesNotExist
from baserow.core.integrations.models import Integration
from baserow.core.integrations.registries import IntegrationType
from baserow.core.models import Application
from baserow.core.registries import application_type_registry
from baserow.core.utils import extract_allowed

from .types import IntegrationForUpdate


class IntegrationHandler:
    def get_integration(
        self, integration_id: int, base_queryset: Optional[QuerySet] = None
    ) -> Integration:
        """
        Returns an integration instance from the database.

        :param integration_id: The ID of the integration.
        :param base_queryset: The base queryset use to build the query if provided.
        :raises IntegrationDoesNotExist: If the integration can't be found.
        :return: The specific integration instance.
        """

        queryset = (
            base_queryset if base_queryset is not None else Integration.objects.all()
        )

        try:
            integration = (
                queryset.select_related("application", "application__workspace")
                .get(id=integration_id)
                .specific
            )
        except Integration.DoesNotExist:
            raise IntegrationDoesNotExist()

        return integration

    def get_integration_for_update(
        self, integration_id: int, base_queryset: Optional[QuerySet] = None
    ) -> IntegrationForUpdate:
        """
        Returns an integration instance from the database that can be safely updated.

        :param integration_id: The ID of the integration.
        :param base_queryset: The base queryset use to build the query if provided.
        :raises IntegrationDoesNotExist: If the integration can't be found.
        :return: The integration instance.
        """

        queryset = (
            base_queryset if base_queryset is not None else Integration.objects.all()
        )

        queryset = queryset.select_for_update(of=("self",))

        return self.get_integration(
            integration_id,
            base_queryset=queryset,
        )

    def get_integrations(
        self,
        application: Application,
        base_queryset: Optional[QuerySet] = None,
        specific: bool = True,
    ) -> Union[QuerySet[Integration], Iterable[Integration]]:
        """
        Gets all the specific integrations of a given application.

        :param application: The application that holds the integrations.
        :param base_queryset: The base queryset to use to build the query.
        :param specific: Whether to return the generic integrations or the specific
            instances.
        :return: The integrations of that application.
        """

        queryset = (
            base_queryset if base_queryset is not None else Integration.objects.all()
        )

        queryset = queryset.filter(application=application)

        if specific:
            queryset = queryset.select_related("content_type")
            return specific_iterator(queryset)
        else:
            return queryset

    def create_integration(
        self,
        integration_type: IntegrationType,
        application: Application,
        before=None,
        **kwargs
    ) -> Integration:
        """
        Creates a new integration for an application.

        :param integration_type: The type of the integration.
        :param application: The application the integration exists in.
        :param before: The integration before which we want to create the integration.
            If not provided, the integration is added as last one.
        :param kwargs: Additional attributes of the integration.
        :raises CannotCalculateIntermediateOrder: If it's not possible to find an
            intermediate order. The full order of the integration of the application
            must be recalculated in this case before calling this method again.
        :return: The created integration.
        """

        application_type = application_type_registry.get_by_model(
            application.specific_class
        )

        if not application_type.supports_integrations:
            raise ApplicationOperationNotSupported()

        if before:
            order = Integration.get_unique_order_before_integration(before)
        else:
            order = Integration.get_last_order(application)

        shared_allowed_fields = ["type", "name"]
        allowed_values = extract_allowed(
            kwargs, shared_allowed_fields + integration_type.allowed_fields
        )

        model_class = cast(Integration, integration_type.model_class)

        integration = model_class(
            application=application, order=order, **allowed_values
        )
        integration.save()

        return integration

    def delete_integration(self, integration: Integration):
        """
        Deletes an integration.

        :param integration: The to-be-deleted integration.
        """

        integration.delete()

    def update_integration(
        self,
        integration_type: IntegrationType,
        integration: IntegrationForUpdate,
        **kwargs
    ) -> Integration:
        """
        Updates and integration with values. Will also check if the values are allowed
        to be set on the integration first.

        :param integration: The integration that should be updated.
        :param values: The values that should be set on the integration.
        :return: The updated integration.
        """

        shared_allowed_fields = ["name"]
        allowed_updates = extract_allowed(
            kwargs, shared_allowed_fields + integration_type.allowed_fields
        )

        for key, value in allowed_updates.items():
            setattr(integration, key, value)

        integration.save()

        return integration

    def move_integration(
        self, integration: IntegrationForUpdate, before: Optional[Integration] = None
    ) -> Integration:
        """
        Moves the given integration before the specified `before` integration in the
        same application.

        :param integration: The integration to move.
        :param before: The integration before which to move the `integration`. If
            before is not specified, the integration is moved at the end of the list.
        :raises CannotCalculateIntermediateOrder: If it's not possible to find an
            intermediate order. The full order of the integration of the application
            must be recalculated in this case before calling this method again.
        :return: The moved integration.
        """

        if before:
            integration.order = Integration.get_unique_order_before_integration(before)
        else:
            integration.order = Integration.get_last_order(integration.application)

        integration.save()

        return integration

    def recalculate_full_orders(
        self,
        application: Application,
    ):
        """
        Recalculates the order to whole numbers of all integrations of the given
        application.
        """

        Integration.recalculate_full_orders(
            queryset=Integration.objects.filter(application=application)
        )
