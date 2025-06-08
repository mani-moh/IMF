
def check(perm):
    def decorater(func):
        def wrapper():
            if perm == "true":
                print("cant")
                return
            else:
                func()
        return wrapper
    return decorater
@check("false")
def add_x():
    print('add x')

add_x()