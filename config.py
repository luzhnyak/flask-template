# Configurations App
class Config(object):

    # Secret Key Flask
    secret_key = "hjhxc83p38c2pc8y8yn23phx8y2398xrmdgFfh788&(08GkyfGuygljljweekjrlwerw"

    domen = "e9d9446de789.ngrok.io"
    emodji = ["😄", "😛️", "😁️", "😢️", "😠️", "🐟️", "🎣️", "😍", "😎", "😠", "👿", "🐡", "🐠", "👍", "👎", "🎂", "🍹", "🍻", "🚗", "🚌", "🚲", "🚋", "⛵", "🌻"]

    # administrator list
    ADMINS = ['oleg.luzhnyak@gmail.com']

    # API    
    OAUTH_CLIENT_ID = "243139916481-6golmha0vgdvkj3qam2ajejkmdjc9ecm.apps.googleusercontent.com"
    OAUTH_SECRET = "p7tLZ07TuYSA-xhm3kMzJcWJ"
    FB_CLIENT_ID = "474089013920675"
    FB_SECRET = "43609a658c8d62b74ed12cbd9d7c44e2"    

    # RECAPTCHA
    GOOGLE_RECAPTCHA_SITE_KEY = "6LcML-4ZAAAAAHCpUCoo-s2GDSnhOj00bV4jY6XR"
    GOOGLE_RECAPTCHA_SECRET_KEY = "6LcML-4ZAAAAANemptItzYBqkciHRr4IgwMM1zrW"

    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    # Folder
    app_folder = "/media/sf_web/flask-start.loc/app"
    images_folder = "/static/img"
    full_images_folder = app_folder + images_folder
