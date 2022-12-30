<div align="center">
In the name of God of the rainbow

<h1><img style="vertical-align:middle" src="https://user-images.githubusercontent.com/117530839/210110357-84313912-9748-4148-9d6a-3486bafa8a87.png"> Kian</h1>

[![](https://img.shields.io/github/v/release/bsimjoo-official/kian?include_prereleases&label=latest%20pre-release)](https://github.com/bsimjoo-official/kian/releases)

Kian is an network-based program to help teachers, which was started with purpose of making attendance smart.

This app will use an **Access-point** ([why?](#why-does-this-app-uses-an-access-point)) and Flask as HTTP backend.
Students should connect to the access point and enter server IP address in the browser, then for the first time they must submit their student number, application will save their MAC address and the student code for future.

https://user-images.githubusercontent.com/117530839/206903458-cf13800f-15a6-43e0-88d4-187c0e0cd1ca.mp4

*A demo of logging-in as BSimjoo*

</div>

## Features
The Kian project has just started and has a good potential for development. Currently, the available features are as follows
 - Suitable for classes with a large number of students.
 - Simple and modern user interface.
 - Easy to use and set up
 - Support for mobile phones
 - Ability to grade and announce grades
 - Registration of attendance history and the history of the device used
 - Prevent unauthorized registration of attendance for several students from one device ([Read more](#why-does-this-app-uses-an-access-point))


## Who or What is Kian?

While I am developing this software, protests continue in Iran and innocent people and children are being injured or murdered by the regime. The name Kian was chosen to commemorate the memory of Kian Pirfalak, the 9 years old child who was killed in Iran's protests by the regime forces.


## Why does this app uses an Access-point?

To prevent students from registering attendance of others and speeding up the process, we need a fixed and unique identifier. Nowadays most phones have a fixed and unique MAC address and it is accessible for the host when there is a direct connection.

As far as I know other ways like using cookies or browser storage are much more easier to get compromised. However, there are other ways to bypass this program. Nevertheless, MAC addresses can be changed (hard or very hard but not impossible). Students can bring their absent classmates' phones, or use their second device as their friend's device. But these make a fake presence status hard and expensive enough.

## License

This software is under GNU General Public License version 3 or (at your option) any later version. See LICENSE.

##### *Thanks to [@farooqkz](https://github.com/farooqkz) for reading and editing documents*
