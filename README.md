# Neuro's Canvas

This is a basic painting app built in [Pygame](https://www.pygame.org/docs/) that allows [Neuro-sama](https://www.bloomberg.com/news/newsletters/2023-06-16/neuro-sama-an-ai-twitch-influencer-plays-minecraft-sings-karaoke-loves-art) to draw. It uses the [Python SDK](https://github.com/CoolCat467/Neuro-API) of the [Neuro API](https://github.com/VedalAI/neuro-game-sdk).

<p align="center">
  <img src="https://raw.githubusercontent.com/Kaya-Kaya/neuro-canvas/main/example_images/jippity_sample.png" alt="A landscape drawn by Jippity" width="50%"/><br>
  A "landscape" drawn by Jippity using this app.
</p>

## Installation
`pip install neuro-canvas`

## Usage
`neuro-canvas`

## Features
### Drawing:
- Straight line
- Sequence of straight lines
- Circle
- Rectangle
- Curve

### Actions:
- Set background color (preset + custom)
- Set brush color (preset + custom)
- Undo

> [!NOTE]
> Pygame does not support anti-aliased curves, so they will appear pixelated. I may implement my own curve function at some point to fix this.

## Contributing
Suggestions and pull requests are welcome!
