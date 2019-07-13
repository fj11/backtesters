# BACKTESTER

> Backtester is a financial research system which can help you analysis the stock, option and future.

## Advantage
* Contains the whole history data of the market
* Has abundant financial index
* Generate market order by manual or by signal
* Create strategy without code
* Strategy can be saved 

## Requirements

1. [Python3.7](https://www.python.org/downloads/release/python-370/)
2. [Pyside2](https://doc.qt.io/qtforpython/index.html#)
3. [Pandas](https://pandas.pydata.org/)
4. [Numpy](https://www.numpy.org/)
5. [Matplotlib](https://matplotlib.org/)
6. [TA-lib](https://mrjbq7.github.io/ta-lib/)
7. [pysqlcipher3](https://github.com/rigglemania/pysqlcipher3)
8. [Pyinstaller](https://www.pyinstaller.org/)
9. [Visual Studio Build Tools 2013](https://support.microsoft.com/en-us/help/3179560/update-for-visual-c-2013-and-visual-c-redistributable-package)
10. [Visual Studio Build Tools 2019](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16)
11. [wmi](https://pypi.org/project/WMI/)
12. [pywin32](https://pypi.org/project/pywin32/) 

## Setup

```bat
> setup.bat
```

* [ta-lib install package](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
* sqlcipher - 32 Bit Windows Setup Instructions (using Visual Studio)
    * Install Visual Studio 2015/2019
    * Install OpenSSL: you can either download the source and build locally or install a prebuilt OpenSSL binary from https://slproweb.com/products/Win32OpenSSL.html (use the latest version)
    * Confirm that the OPENSSL_CONF environment variable is set properly: this should not be root OpenSSL path (ex: C:\openssl-Win32), but instead should be the path to the config file (ex: C:\openssl-Win32\bin\openssl.cfg)
    * Copy the OpenSSL folder (C:\openssl-Win32\include\openssl) to the VC include directory (ex: C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\include): confirm the following path exists (\VC\include\openssl\aes.h)
    * Install the latest version of Python 3 (32-bit): if you have Python 64-bit installed, you may have to uninstall it before installing Python 32-bit.
    * Use the SQL Cipher 3 amalgamation: if needed, directions for building SQL Cipher can be found on the following tutorial: http://www.jerryrw.com/howtocompile.ph
    * Follow the general instructions for building the amalgamation
* pysqlciphr3
    ```bat
    > python setup.py build_amalgamation
    > python setup.py install
    ```

##  Tested Platforms

* Windows(32bit/64bit)
> * Windows XP or newer

## Data provider

* Rqdata
    * [Documents](https://www.ricequant.com/doc/rqdata-institutional)

## Build

> Double click makefile.bat or execute makefile.bat in command line mode to run the building process
```bat
> makefile.bat
```

## Test
> Double click test.bat or execute test.bat in command line mode to run the automation test process
```bat
> test.bat
```