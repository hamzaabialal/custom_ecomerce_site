from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserTemplateForm
from .models import UserTemplate
import charset_normalizer  # Install with `pip install charset-normalizer`


def read_file(file):
    """
    Reads file content with automatic encoding detection.
    Uses charset_normalizer for encoding detection and fallback if needed.
    """
    raw_data = file.read()
    result = charset_normalizer.detect(raw_data)
    encoding = result['encoding'] or 'utf-8'  # Default to utf-8 if detection fails

    try:
        # Try to decode with detected encoding
        return raw_data.decode(encoding)
    except (UnicodeDecodeError, TypeError):
        # If the detected encoding doesn't work, fallback to a different encoding
        return raw_data.decode('ISO-8859-1', errors='ignore')


class UploadTemplateView(LoginRequiredMixin, FormView):
    template_name = 'upload_template.html'
    form_class = UserTemplateForm

    def form_valid(self, form):
        # Read file content
        html_file = self.request.FILES['html_file']
        css_file = self.request.FILES['css_file']
        js_file = self.request.FILES['js_file']

        try:
            html_content = read_file(html_file)
            css_content = read_file(css_file)
            js_content = read_file(js_file)

            # Save to the database
            user_template = UserTemplate.objects.create(
                user=self.request.user,
                html_content=html_content,
                css_content=css_content,
                js_content=js_content,
            )

            # Redirect to the template view with pk
            return redirect('view_template', pk=user_template.id)

        except UnicodeDecodeError as e:
            # Log error or notify user
            return HttpResponse(f"Error reading file: {str(e)}", status=400)

from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class ViewTemplateView(LoginRequiredMixin, DetailView):
    model = UserTemplate
    context_object_name = 'user_template'
    template_name = 'view_template.html'

    def get_queryset(self):
        """
        Restrict access to templates owned by the logged-in user.
        """
        return UserTemplate.objects.filter(user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        """
        Render the user template with embedded CSS and JavaScript.
        Add custom JavaScript for Add to Cart functionality.
        """
        user_template = context['user_template']

        # Retrieve the content from the database
        html_content = user_template.html_content
        css_content = user_template.css_content
        js_content = user_template.js_content

        # Construct the complete HTML with embedded CSS and JavaScript
        full_html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>User Template</title>
            <style>{css_content}</style>
            <script>
                {js_content}

                // Custom JavaScript for Add to Cart functionality
                document.addEventListener('DOMContentLoaded', function() {{
                    console.log('Page loaded, JavaScript initialized.');

                    const addToCartButtons = document.querySelectorAll('.add-to-cart');
                    console.log('Add to Cart buttons found:', addToCartButtons.length);

                    addToCartButtons.forEach(button => {{
                        button.addEventListener('click', function() {{
                            const productName = this.getAttribute('data-product-name');
                            const productPrice = this.getAttribute('data-product-price');
                            console.log('Adding to cart:', productName, productPrice);

                            // Make an AJAX POST request to add the product to the cart
                            fetch('/add-to-cart/', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCookie('csrftoken'),
                                }},
                                body: JSON.stringify({{
                                    product_name: productName,
                                    product_price: productPrice,
                                    quantity: 1
                                }})
                            }})
                            .then(response => response.json())
                            .then(data => {{
                                if (data.message) {{
                                    alert(data.message); // Success message
                                }} else if (data.error) {{
                                    alert('Error: ' + data.error); // Error message
                                }}
                            }})
                            .catch(error => {{
                                console.error('Error:', error);
                            }});
                        }});
                    }});

                    // Helper function to get CSRF token
                    function getCookie(name) {{
                        let cookieValue = null;
                        if (document.cookie && document.cookie !== '') {{
                            const cookies = document.cookie.split(';');
                            for (let i = 0; i < cookies.length; i++) {{
                                const cookie = cookies[i].trim();
                                if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                    break;
                                }}
                            }}
                        }}
                        return cookieValue;
                    }}
                }});
            </script>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        return HttpResponse(full_html_content)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cart

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_name = data.get("product_name")
            product_price = data.get("product_price")
            quantity = data.get("quantity", 1)

            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated."}, status=403)

            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product_name=product_name,
                defaults={"product_price": product_price, "quantity": quantity},
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({"message": "Product added to cart successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

