def utf16_to_utf8(old_path,new_path):
    try:
        with open(old_path, "rb") as source:
            with open(new_path, "wb") as dest:
                dest.write(source.read().decode("utf-16").encode("utf-8"))
        return "OK"
    except FileNotFoundError:
        return "NOT OK"