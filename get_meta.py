import subprocess, os

def get_imagemeta(source):
    binary = os.path.join(os.getcwd(), 'imagemagick\\identify.exe')
    p=subprocess.run(f'{binary} -verbose "{source}"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode()
    
    


print(os.getcwd())
    
print(get_imagemeta("D:/autocad2013/Autodesk® AutoCAD 2013 Korean Win 64bit/x64/InventorFusion/CommAppDat/Autodesk/Inventor Fusion 2013/Design Data/Texture Image/Brick06.JPG"))