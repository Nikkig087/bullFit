from django import template
from cloudinary import CloudinaryImage

register = template.Library()

@register.simple_tag
def webp(cloudinary_url, width=250, height=None):
    """
    Generate a Cloudinary URL for an image in WebP format.

    This template tag takes a Cloudinary image URL and transforms it
    into a WebP format URL with optional resizing.

    Args:
        cloudinary_url (str): The original Cloudinary URL of the image.
        width (int, optional): The desired width of the output image.
            Defaults to 250.
        height (int, optional): The desired height of the output image.
            If not specified, the height will be determined based on the 
            aspect ratio.

    Returns:
        str: The transformed WebP image URL, or an empty string if 
        the input URL is invalid.
    """
    if not cloudinary_url:
        return ""

    public_id = cloudinary_url.split('/')[-1].split('.')[0]

    transformation = {'format': 'webp', 'width': width, 'crop': 'fit'}
    if height:
        transformation['height'] = height

    webp_url = CloudinaryImage(public_id).build_url(**transformation)
    
    return webp_url
