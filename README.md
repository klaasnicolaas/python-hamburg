<!-- Banner -->
![alt Banner of the Hamburg package](https://raw.githubusercontent.com/klaasnicolaas/python-hamburg/main/assets/header_hamburg-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Code Quality][code-quality-shield]][code-quality]
[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]

[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]

Asynchronous Python client for the urban datasets of Hamburg (Germany).

## About

A python package with which you can retrieve data from the Urban Data Platform of Hamburg via [their API][api]. This package was initially created to only retrieve parking data from the API, but the code base is made in such a way that it is easy to extend for other datasets from the same platform.

## Installation

```bash
pip install hamburg
```

## Datasets

You can read the following datasets with this package:

- [Disabled parking spaces / Behindertenstellplätze][disabled_parking] (813)
- [Park and rides occupancy / Park + Ride Anlagen][park_and_ride] (32)
- [Garages occupancy / Parkhäuser][garages] (45 live data / 124 total)

There are a number of parameters you can set to retrieve the data:

- **limit** (default: 10) - How many results you want to retrieve.
- **bulk** (default: false) - If string is true, number of rows will be ignored and the entire result will be returned.

<details>
    <summary>Click here to get more details</summary>

### Disabled parking spaces

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `spot_id` | string | The ID of the parking spot |
| `street` | string | The street name |
| `limitation` | string | Some locations have window times where the location is only specific for disabled parking, outside these times everyone is allowed to park there |
| `number` | string | The number of parking spots on this location |
| `longitude` | float | The longitude of the parking spot |
| `latitude` | float | The latitude of the parking spot |

### Park and Rides

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `spot_id` | string | The ID of the park and ride |
| `name` | string | The name of the park and ride |
| `park_type` | string | The parking type of the park and ride |
| `address` | string | The address of the park and ride |
| `construction_year` | string | The year the park and ride was constructed |
| `public_transport_line` | string | The public transport line the park and ride is connected to |
| `disabled_parking_spaces` | int | The number of disabled parking spaces on the park and ride |
| `tickets` | dict | The type of tickets available for the park and ride |
| `url` | string | The URL of the park and ride where you can find more information |
| `free_space` | int | The number of free spaces on the park and ride |
| `capacity` | int | The capacity of the park and ride |
| `availability_pct` | float | The percentage of the park and ride that is available |
| `longitude` | float | The longitude of the park and ride |
| `latitude` | float | The latitude of the park and ride |
| `updated_at` | datetime | The date and time the park and ride was last updated |

### Garages

Extra parameters to filter the data:

- **available** (default: None) - Allows you to filter based on available spaces, using operators such as `<`, `<=`, `>` and `>=`.

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `spot_id` | string | The ID of the garage |
| `name` | string | The name of the pgarage |
| `park_type` | string | The parking type of the garage |
| `disabled_parking_spaces` | int | The number of disabled parking spaces in the garage |
| `status` | string | The status of the garage (**frei**, **nahezu belegt**, **besetzt** or **keine Auslastungsdaten**) |
| `address` | string | The address of the garage |
| `price` | string | The price list that is used for parking in a garage |
| `data_origin` | string | Where data originally comes from |
| `free_space` | int | The number of free spaces in the garage |
| `capacity` | int | The capacity of the garage |
| `availability_pct` | float | The percentage that is still available in the garage |
| `longitude` | float | The longitude of the garage |
| `latitude` | float | The latitude of the garage |
| `updated_at` | datetime | The date and time the garage was last updated |

</details>

## Example

```python
import asyncio

from hamburg import UDPHamburg


async def main() -> None:
    """Show example on using the UDP Hamburg API client."""
    async with UDPHamburg() as client:
        disabled_parkings = await client.disabled_parkings()
        park_and_rides = await client.park_and_rides()
        garages = await client.garages()
        print(disabled_parkings)
        print(park_and_rides)
        print(garages)


if __name__ == "__main__":
    asyncio.run(main())
```

## Use cases

[NIPKaart.nl][nipkaart]

A website that provides insight into where disabled parking spaces are, based on data from users and municipalities. Operates mainly in the Netherlands, but also has plans to process data from abroad.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.9+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## License

MIT License

Copyright (c) 2022-2023 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[api]: https://api.hamburg.de/datasets/v1/
[nipkaart]: https://www.nipkaart.nl

[disabled_parking]: https://api.hamburg.de/datasets/v1/behindertenstellplaetze
[park_and_ride]: https://api.hamburg.de/datasets/v1/p_und_r
[garages]: https://api.hamburg.de/datasets/v1/parkhaeuser

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-hamburg/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-hamburg/actions/workflows/tests.yaml
[code-quality-shield]: https://github.com/klaasnicolaas/python-hamburg/actions/workflows/codeql.yaml/badge.svg
[code-quality]: https://github.com/klaasnicolaas/python-hamburg/actions/workflows/codeql.yaml
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-hamburg.svg
[commits-url]: https://github.com/klaasnicolaas/python-hamburg/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-hamburg/branch/main/graph/badge.svg?token=4Y4YAYHR2D
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-hamburg
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-hamburg
[downloads-shield]: https://img.shields.io/pypi/dm/hamburg
[downloads-url]: https://pypistats.org/packages/hamburg
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-hamburg.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-hamburg.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2023.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/5041849456b7348f3bc7/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-hamburg/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/hamburg/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/hamburg
[typing-shield]: https://github.com/klaasnicolaas/python-hamburg/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-hamburg/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-hamburg.svg
[releases]: https://github.com/klaasnicolaas/python-hamburg/releases

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
