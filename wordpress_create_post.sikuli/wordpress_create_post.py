type("Username.png", "admin")
type("Password.png", "compilerz")
click("1333984910768.png")
wait("WORDPRESSVer.png",10)
wait(1) # Sometimes the remember password ribbon takes a while
        # to show up and throws everything off, this fixes that
        # problem
hover("1333985696030.png")
click("AddNew.png")
wait("AddNewPost.png",10)
type("Entertitlehe.png", "Free Cups at the Fence!")
type("B1EiE4iiiL.png", "In honor of the gift from Bill, these cups are being given out")
click("BI.png")
type("Inhonorofthe.png", " by the fence")
click("1.png")
type("B1EiE4sInhon.png", ":\n")
click("UploadInsert.png")

nautilus = App("drag_drop_cup_picture")
nautilus.open("/usr/bin/nautilus ~/Pictures")
dragDrop("IMG201109071.png", "1333988669860.png")
nautilus.close()
click("Dropfilesher.png")
type(Key.PAGE_DOWN)
type(Key.PAGE_DOWN)
click("1333989030349.png")
type(Key.PAGE_UP)
type(Key.PAGE_UP)
wait("lurl.png")
type(Key.ENTER)
click("I.png")
type("GET THEM WHILE THEY ARE HOT!")
try:
    click("1333989103045.png")
except:
    click("1333989103045.alt.png")
wait("LAddNewPostC.png")
click("1333989935449.png")

