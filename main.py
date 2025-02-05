import whisper
import ffmpeg
import os
from enum import Enum
from typing import Optional

class PresetStyle(Enum):
    MODERN = {
        'fontName': 'Helvetica',
        'fontSize': 26,
        'primaryColor': '#FFFFFF',
        'outlineColor': '#000000',
        'outlineWidth': 1.5,
        'alignment': 2,
        'bold': False
    }
    MOVIE = {
        'fontName': 'Arial',
        'fontSize': 28,
        'primaryColor': '#FFFF00',
        'outlineColor': '#000000',
        'outlineWidth': 2,
        'alignment': 2,
        'bold': True
    }
    MINIMAL = {
        'fontName': 'Roboto',
        'fontSize': 24,
        'primaryColor': '#FFFFFF',
        'outlineColor': '#000000',
        'outlineWidth': 1,
        'alignment': 2,
        'bold': False
    }
    PRESENTATION = {
        'fontName': 'Calibri',
        'fontSize': 32,
        'primaryColor': '#FFFFFF',
        'outlineColor': '#000000',
        'outlineWidth': 1,
        'alignment': 1,
        'bold': True
    }
    RETRO = {
        'fontName': 'Courier New',
        'fontSize': 30,
        'primaryColor': '#00FF00',
        'outlineColor': '#000000',
        'outlineWidth': 2,
        'alignment': 2,
        'bold': False
    }

class SubtitleStyle:
    def __init__(self, 
                 fontName: str = 'Arial',
                 fontSize: int = 24,
                 primaryColor: str = '#FFFFFF',
                 outlineColor: str = '#000000',
                 outlineWidth: float = 2,
                 alignment: int = 2,
                 bold: bool = False):
        self.fontName = fontName
        self.fontSize = fontSize
        self.primaryColor = self._format_color(primaryColor)
        self.outlineColor = self._format_color(outlineColor)
        self.outlineWidth = outlineWidth
        self.alignment = alignment
        self.bold = bold

    @staticmethod
    def _format_color(color: str) -> str:
        if color.startswith('#'):
            hex_str = color[1:]
            if len(hex_str) == 6:
                rr = hex_str[0:2]
                gg = hex_str[2:4]
                bb = hex_str[4:6]
                return f"&H00{bb}{gg}{rr}"
            return color
        return color

    @classmethod
    def from_preset(cls, preset: PresetStyle):
        return cls(**preset.value)

    def get_style_string(self, srtPath: str) -> str:
        return (f"subtitles={srtPath}:"
                f"force_style='"
                f"Fontname={self.fontName},"
                f"FontSize={self.fontSize},"
                f"PrimaryColour={self.primaryColor},"
                f"OutlineColour={self.outlineColor},"
                f"Outline={self.outlineWidth},"
                f"Alignment={self.alignment},"
                f"Bold={1 if self.bold else 0}'")

class Extractor:
    def get_audio(self, videoPath: str, audioPath: str = "output.mp3") -> str:
        if not os.path.exists(videoPath):
            raise FileNotFoundError(f"Video file not found: {videoPath}")
        try:
            ffmpeg.input(videoPath).output(audioPath, format='mp3', acodec='mp3').run(overwrite_output=True, quiet=True)
            return audioPath
        except Exception as e:
            raise RuntimeError(f"Error extracting audio: {e}")

    def get_words(self, audioPath: str) -> list:
        if not os.path.exists(audioPath):
            raise FileNotFoundError(f"Audio file not found: {audioPath}")
        try:
            model = whisper.load_model("medium")
            result = model.transcribe(audio=audioPath, word_timestamps=True)
            return [word for segment in result['segments'] for word in segment['words']]
        except Exception as e:
            raise RuntimeError(f"Error during transcription: {e}")

    def format_time(self, timeInSeconds: float) -> str:
        milliSeconds = int((timeInSeconds % 1) * 1000)
        seconds = int(timeInSeconds)
        return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02},{milliSeconds:03}"

    def get_srt(self, wordList: list, outputPath: str = "output.srt") -> str:
        if not wordList:
            raise ValueError("No words to save in SRT file.")
        try:
            with open(outputPath, "w", encoding="utf-8") as file:
                for wordIndex, word in enumerate(wordList, start=1):
                    file.write(f"{wordIndex}\n{self.format_time(word['start'])} --> {self.format_time(word['end'])}\n{word['word'].strip()}\n\n")
            return outputPath
        except Exception as e:
            raise RuntimeError(f"Error writing SRT file: {e}")

class VideoProcessor:
    def add_subtitles(self, videoPath: str, srtPath: str, subtitleStyle: Optional[SubtitleStyle] = None, outputPath: str = "output_with_subs.mp4") -> str:
        if not os.path.exists(videoPath):
            raise FileNotFoundError(f"Video file not found: {videoPath}")
        if not os.path.exists(srtPath):
            raise FileNotFoundError(f"Subtitle file not found: {srtPath}")
        try:
            if not subtitleStyle:
                subtitleStyle = SubtitleStyle.from_preset(PresetStyle.MODERN)
            vfOption = subtitleStyle.get_style_string(srtPath)
            ffmpeg.input(videoPath).output(outputPath, vf=vfOption).run(overwrite_output=True, quiet=True)
            return outputPath
        except Exception as e:
            raise RuntimeError(f"Error adding subtitles: {e}")

def main():
    extractorObj = Extractor()
    processorObj = VideoProcessor()
    try:
        subtitleStyle = SubtitleStyle.from_preset(PresetStyle.MOVIE)
        
        audioFile = extractorObj.get_audio("test.mp4")
        wordList = extractorObj.get_words(audioFile)
        srtFile = extractorObj.get_srt(wordList)
        outputVideo = processorObj.add_subtitles(
            videoPath="test.mp4", 
            srtPath=srtFile,
            subtitleStyle=subtitleStyle
        )
        print(f"Video with styled subtitles created: {outputVideo}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    
    main()