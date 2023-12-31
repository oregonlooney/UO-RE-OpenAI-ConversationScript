# Ultima Online OpenAI Conversation Agent
[![uo-openai-pic1.png](https://i.postimg.cc/7PWp3YPx/uo-openai-pic1.png)](https://postimg.cc/gr3Sdp65)
## Introduction

This project represents an integration of OpenAI's API with Ultima Online, a classic 2D isometric RPG. It forms the base code for an AI-powered conversation agent that interacts with players within the game.

## Purpose

The primary goal of creating this agent was to experiment with Generative AI NPC agents, exploring the possibilities of enhancing game interaction through cutting-edge AI technology. By embedding an AI-driven character within Ultima Online, players can engage in more immersive and dynamic conversations.

## Instructions

Add the script to the Razor Enhanced script menu and add your own OpenAI API key, player names, and keywords.

## Technical Details

### Razor Enhanced Plugin

The script relies on the [Razor Enhanced Plugin](https://razorenhanced.github.io/), providing a macro/scripting interface for Ultima Online using IronPython 3.4. This allows the agent to process and respond to in-game conversations in real-time. 

Due to the limitations of the IronPython 3.4 environment, the implementation does not utilize the standard OpenAI API libraries. Instead, the code leverages the .NET Framework's `System.Net.Http` namespace to handle HTTP requests and responses. 

### Response Mechanism

The agent can be configured to respond to specific players or predefined keywords. It will remember conversations and which player instigated them for a short period of time. 

## Features

- Real-time conversation with players using OpenAI's GPT-3.5-turbo model
- Ability to respond to specific players or keywords
- Configurable personality and behavior

## Usage

This code can be used as a starting point for developers looking to integrate AI-driven NPCs into Ultima Online or similar game environments. By customizing and extending the base code, new and innovative AI-powered game interactions can be created.

## Conclusion

This project illustrates the potential of AI in enhancing player interaction within a classic game like Ultima Online. It opens doors to novel and captivating gaming experiences, marrying traditional gaming with modern AI capabilities.
