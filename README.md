<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
<h3 align="center">VocalScript</h3>

  <p align="center">
    A TTS application
    <br />
    <br />
    <a href="https://github.com/BladerX11/vocalscript/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/BladerX11/vocalscript/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project
### Built With

* [![Python][Python]][Python-url]
* [![Qt][Qt]][Qt-url]
* [![Azure][Azure]][Azure-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

1. An [Azure subscription](https://azure.microsoft.com/free/cognitive-services) and an [AI Services resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry)
2. [ffmpeg](https://ffmpeg.org/download.html) on linux

### Installation

1. Navigate to the [Azure portal](portal.azure.com), then select your speech service resource to view its keys and enpoints.
2. Download the [latest release](https://github.com/BladerX11/vocalscript/releases/latest) for the correct OS, indicated after the application name.

    ![OS indication on release page](assets/release.webp)

3. Launch the application and click on settings in the menubar, then enter your into the respective fields and click save.

    ![Settings button in app](assets/enter-settings.webp)
    ![Settings dialog](assets/settings.webp)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage
### Saving audio

1. Enter the text to be synthesised in the text box.
2. Click the save button below the text box.

    ![Save button in app](assets/save.webp)

3. Audio files will be saved in a folder named saved where your OS data folder is, named with the date and time it was synthesised.
    * Windows: C:\Users\<USER>\AppData\Roaming\vocalscript/vocalscript/saved
    * Linux: ~/.local/share/vocalscript/vocalscript/saved
    * MacOS: ~/Library/Application Support/vocalscript/vocalscript/saved
    
### Playing audio

1. Enter the text to be synthesised in the text box.
2. Click the play button below the text box.

    ![Play button in app](assets/play.webp)

3. The audio will be played through the default audio output of the system.

### Using SSML

1. Enter the SSML content to be synthesised in the text box. (Note: The selected voice above the text box will be ignored with SSML)
2. Check the SSML checkbox below the text box.

    ![SSML checkbox in app](assets/ssml.webp)
  
3. Click the buttons to play or save. The text content will be parsed as SSML.

### Editing API information

The key and endpoint of your API can be edited either through settings in the menubar, or the vocalscript.ini that will be created at the location where you OS stores configurations.

* Linux & MacOS: ~/.config/vocalscript/vocalscript.ini
* Windows: C:\Users\<USER>\AppData\Roaming\vocalscript\vocalscript.ini

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/BladerX11/vocalscript/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=BladerX11/vocalscript" alt="contrib.rocks image" />
</a>

<!-- CONTACT -->
## Contact

Project Link: [https://github.com/BladerX11/vocalscript](https://github.com/BladerX11/vocalscript)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Lucide Icons](https://lucide.dev/icons)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/BladerX11/vocalscript.svg?style=for-the-badge
[contributors-url]: https://github.com/BladerX11/vocalscript/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/BladerX11/vocalscript.svg?style=for-the-badge
[forks-url]: https://github.com/BladerX11/vocalscript/network/members
[stars-shield]: https://img.shields.io/github/stars/BladerX11/vocalscript.svg?style=for-the-badge
[stars-url]: https://github.com/BladerX11/vocalscript/stargazers
[issues-shield]: https://img.shields.io/github/issues/BladerX11/vocalscript.svg?style=for-the-badge
[issues-url]: https://github.com/BladerX11/vocalscript/issues
[Python]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue
[Python-url]: http://python.org/
[Qt]: https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white
[Qt-url]: https://www.qt.io/
[Azure]: https://img.shields.io/badge/microsoft%20azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white
[Azure-url]: https://azure.microsoft.com/
