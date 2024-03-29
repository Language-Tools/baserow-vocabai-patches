from baserow.contrib.builder.elements.models import (
    HeadingElement,
    ImageElement,
    LinkElement,
    ParagraphElement,
)


class ElementFixtures:
    def create_builder_heading_element(self, user=None, page=None, **kwargs):
        element = self.create_builder_element(HeadingElement, user, page, **kwargs)
        return element

    def create_builder_paragraph_element(self, user=None, page=None, **kwargs):
        element = self.create_builder_element(ParagraphElement, user, page, **kwargs)
        return element

    def create_builder_image_element(self, user=None, page=None, **kwargs):
        element = self.create_builder_element(ImageElement, user, page, **kwargs)
        return element

    def create_builder_link_element(self, user=None, page=None, **kwargs):
        element = self.create_builder_element(LinkElement, user, page, **kwargs)
        return element

    def create_builder_element(self, model_class, user=None, page=None, **kwargs):
        if user is None:
            user = self.create_user()

        if not page:
            builder = kwargs.pop("builder", None)
            page_args = kwargs.pop("page_args", {})
            page = self.create_builder_page(user=user, builder=builder, **page_args)

        if "order" not in kwargs:
            kwargs["order"] = model_class.get_last_order(page)

        page = model_class.objects.create(page=page, **kwargs)

        return page
