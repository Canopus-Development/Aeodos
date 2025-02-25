# Aoede Template System

## Overview
Aoede uses a modular template system to create dynamic, responsive websites. It combines standard HTML/CSS with AI-driven layout suggestions.

## Template Hierarchy
```
templates/
├── base/          # Base template files
├── components/    # Reusable components
├── layouts/       # Page layouts
└── pages/         # Page-specific templates
```

## Template Structure
Base template example:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    {% raw %}{{ meta_tags }}{% endraw %}
    <title>{% raw %}{{ page.title }}{% endraw %}</title>
</head>
<body>
    {% raw %}{% include header.html %}{% endraw %}
    
    <main>
        {% raw %}{{ content }}{% endraw %}
    </main>

    {% raw %}{% include footer.html %}{% endraw %}
</body>
</html>
```

## Components
Example component:

```html
<!-- components/card.html -->
<div class="card">
    <h3>{% raw %}{{ title }}{% endraw %}</h3>
    <p>{% raw %}{{ description }}{% endraw %}</p>
    {% raw %}{% if button %}
    <a href="{{ button.url }}" class="btn">{{ button.text }}</a>
    {% endif %}{% endraw %}
</div>
```

## Page Templates
Example page template:

```html
<!-- pages/home.html -->
{% raw %}{% extends "base.html" %}

{% block content %}
<div class="hero">
    <h1>{{ page.title }}</h1>
    <p>{{ page.description }}</p>
</div>

{% for feature in features %}
    {% include "components/card.html" %}
{% endfor %}
{% endblock %}{% endraw %}
```

## Theme Variables
```css
:root {
    --primary-color: {% raw %}{{ theme.colors.primary }}{% endraw %};
    --secondary-color: {% raw %}{{ theme.colors.secondary }}{% endraw %};
    --font-heading: {% raw %}{{ theme.fonts.heading }}{% endraw %};
    --font-body: {% raw %}{{ theme.fonts.body }}{% endraw %};
}
```

## AI Integration
The AI engine processes these templates by:
1. Analyzing user requirements
2. Selecting appropriate components
3. Injecting dynamic content
4. Optimizing layouts

## Usage Example

```python
from Aoede.template import Template

# Load template
template = Template.load('pages/home.html')

# Generate content
result = template.render({
    'page': {
        'title': 'Welcome',
        'description': 'Modern business website'
    },
    'features': [
        {'title': 'Feature 1', 'description': 'Description 1'},
        {'title': 'Feature 2', 'description': 'Description 2'}
    ],
    'theme': {
        'colors': {
            'primary': '#1A2B3C',
            'secondary': '#4C5D6E'
        }
    }
})
```

## Best Practices

1. Use semantic HTML
2. Keep components modular
3. Follow BEM naming conventions
4. Implement responsive designs
5. Optimize for accessibility

## Template Tags

| Tag | Description |
|-----|-------------|
| {% raw %}{{ variable }}{% endraw %} | Output variable content |
| {% raw %}{% include file %}{% endraw %} | Include template file |
| {% raw %}{% if condition %}{% endraw %} | Conditional rendering |
| {% raw %}{% for item in items %}{% endraw %} | Loop through items |

## Development Notes

- Templates are cached for performance
- Support hot-reloading in development
- Include source maps for debugging
- Validate HTML output

## See Also
- [Development Guide](../development/README.md)
- [Configuration Guide](../configuration/README.md)
- [API Reference](../api-reference/README.md)