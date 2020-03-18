def create_templates_from_data(inputtemplates):
    """Create template objects from data."""
    for input_template in inputtemplates:
        InputTemplate.objects.create(
            template_id=input_template.id,
            format=input_template.formatclass,
            label=input_template.label,
            extension=input_template.extension,
            optional=input_template.optional,
            unique=input_template.unique,
            accept_archive=input_template.acceptarchive,
            corresponding_profile=new_profile,
        )
