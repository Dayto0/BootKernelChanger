# BootKernelChanger

**BootKernelChanger** — An application for modifying the kernel (kernel image) inside `boot.img`.  
It is designed to replace the stock kernel with a custom or already patched one, easier than typing commands in the console.  

---

- GUI built with Tkinter  
- Select `boot.img` and a new kernel (`kernel image`)  
- Automatic unpacking and repacking of `boot.img` using built-in `magiskboot.exe`  
- Log display  
- `.exe` (Windows build)  

---

## Screenshots
![Main window](https://i.imgur.com/xToHaRd_d.webp?maxwidth=760&fidelity=grand)  

---

## Usage

1. Run `BootKernelChanger.exe`.  
2. Select your current `boot.img`.  
3. Select the kernel (`Image`) you want to insert.  
4. Click **Build**.  
5. Save the new `boot.img`.  
