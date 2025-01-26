
# Aeodos Template System

## Overview
Aeodos uses a modular template system to create dynamic, responsive websites. It combines standard HTML/CSS with AI-driven layout suggestions.

## Template Hierarchy
- **Base Templates**: Contains global elements (header, footer).  
- **Partial Templates**: Smaller components (navbars, modals).  
- **Page Templates**: Specific pages (home, about, contact).

## Template Fields
- Allows placeholders for AI-injected content (e.g., {{ content }}).
- Jinja2 is used to process these placeholders.

## Customizing Templates
- Create new templates in the `app/templates/` directory.
- Use partials for repeatable sections.
- Include custom CSS/JS in the `<head>` or `<body>` as needed.

## AI Integration
1. The AI engine parses user preferences.  
2. Suggestions are inserted into placeholders.  
3. Final HTML is generated and stored or returned to the user.

## Example
```html
<!-- ...existing code... -->
<body>
  <header>
    {% include 'partials/header.html' %}
  </header>

  <main>
    {{ body_content }}
  </main>

  <footer>
    {% include 'partials/footer.html' %}
  </footer>
</body>
<!-- ...existing code... -->
```

## Reusability & Theming
- Use theme variables in CSS:
  ```css
  :root {
    --primary-color: #1A2B3C;
    // ...existing code...
  }
  ```
- Switch themes via environment variables or config.

## Next Steps
- [Development Guide](../development/README.md)
- [Deployment Guide](../deployment/README.md)
- [Testing Guide](../testing/README.md)