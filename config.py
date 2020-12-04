# Configurations App
class Config(object):

    # Secret Key Flask
    secret_key = "hjhxc83p38c2pc8y8yn23phx8y2398xrmdgFfh788&(08GkyfGuygljljweekjrlwerw"

    domen = "flask-satart.loc"
    emodji = ["😄", "😛️", "😁️", "😢️", "😠️", "🐟️", "🎣️", "😍", "😎", "😠", "👿", "🐡", "🐠", "👍", "👎", "🎂", "🍹", "🍻", "🚗", "🚌", "🚲", "🚋", "⛵", "🌻"]

    # administrator list
    ADMINS = ['oleg.luzhnyak@gmail.com']

    # RECAPTCHA
    GOOGLE_RECAPTCHA_SITE_KEY = "6LcML-4ZAAAAAHCpUCoo-s2GDSnhOj00bV4jY6XR"
    GOOGLE_RECAPTCHA_SECRET_KEY = "6LcML-4ZAAAAANemptItzYBqkciHRr4IgwMM1zrW"

    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    # Folder
    app_folder = "/media/sf_web/flask-start.loc/app"
    images_folder = "/static/img"
    full_images_folder = app_folder + images_folder
