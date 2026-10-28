#!/usr/bin/env python3
"""多格式文件解析脚本（zion-assets 与 zion-storyboard 共用，内容一致）

支持：
- TXT：多编码读取
- DOCX：按正文顺序提取段落及表格（含嵌套表格）文本
- PDF：PyMuPDF (fitz) -> pdfplumber -> PyPDF2 多级回退
- MP4/MOV/AVI/MKV/WEBM：ffprobe 元数据；可选抽帧（--video-frames）或抽音频（--extract-audio）
- --structure：尝试解析剧本结构（场次、角色、对白）

用法：
  python parse_input.py <file_path> [--output <path>] [--type pdf|txt|docx|video|auto]
  python parse_input.py <file_path> --video-frames <dir> [--frame-interval <s>]
  python parse_input.py <file_path> --extract-audio
  python parse_input.py <file_path> --structure
"""

import argparse
import json
import math
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def parse_txt(file_path: str) -> str:
    """读取 TXT 文件内容，尝试多种编码"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'utf-16', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def parse_docx(file_path: str) -> str:
    """Extract body paragraphs and table cells in document order."""
    try:
        import docx
        from docx.oxml.ns import qn
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        doc = docx.Document(file_path)

        def blocks(element):
            for child in element.iterchildren():
                if child.tag == qn('w:p'):
                    text = Paragraph(child, doc).text
                    if text.strip():
                        yield text
                elif child.tag == qn('w:tbl'):
                    for row in Table(child, doc).rows:
                        seen, cells = set(), []
                        for cell in row.cells:
                            if cell._tc in seen:
                                continue
                            seen.add(cell._tc)
                            cells.append('\n'.join(blocks(cell._tc)))
                        if any(text.strip() for text in cells):
                            yield '\t'.join(cells)

        return '\n\n'.join(blocks(doc.element.body))
    except ImportError:
        return "[WARNING] 未安装 python-docx，无法解析 DOCX。请安装: pip install python-docx\n[FILE_PATH] " + file_path


def parse_pdf(file_path: str) -> str:
    """提取 PDF 文本，fitz -> pdfplumber -> PyPDF2 多级回退"""
    available_engines = []
    try:
        import fitz
        available_engines.append('PyMuPDF')
        text_parts = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        content = '\n\n'.join(text_parts)
        if content.strip():
            return content
    except ImportError:
        pass
    except Exception:
        pass

    try:
        import pdfplumber
        available_engines.append('pdfplumber')
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        content = '\n\n'.join(text_parts)
        if content.strip():
            return content
    except ImportError:
        pass
    except Exception:
        pass

    try:
        import PyPDF2
        available_engines.append('PyPDF2')
        text_parts = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        content = '\n\n'.join(text_parts)
        if content.strip():
            return content
    except ImportError:
        pass
    except Exception:
        pass

    if available_engines:
        return "[WARNING] 已尝试的 PDF 提取器未取得可用文本；请检查文件、加密状态或是否需要 OCR。\n[FILE_PATH] " + file_path
    return "[WARNING] 未安装 PyMuPDF / pdfplumber / PyPDF2，无法解析 PDF。请安装: pip install PyMuPDF\n[FILE_PATH] " + file_path


def get_video_metadata(file_path: str) -> dict:
    """使用 ffprobe 获取视频元数据"""
    metadata = {
        'file_path': file_path,
        'file_name': os.path.basename(file_path),
        'file_size_bytes': os.path.getsize(file_path),
        'duration_seconds': 0,
        'width': 0,
        'height': 0,
        'fps': 0,
        'codec': '',
        'bit_rate': 0,
        'has_audio': False,
    }

    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            metadata['error'] = "ffprobe 执行失败: " + result.stderr
            return metadata

        data = json.loads(result.stdout)
        fmt = data.get('format', {})
        metadata['duration_seconds'] = round(float(fmt.get('duration', 0)), 2)
        metadata['bit_rate'] = int(fmt.get('bit_rate', 0))
        metadata['format_name'] = fmt.get('format_name', '')

        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video' and not metadata.get('width'):
                metadata['width'] = stream.get('width', 0)
                metadata['height'] = stream.get('height', 0)
                metadata['codec'] = stream.get('codec_name', '')
                fps_str = stream.get('r_frame_rate', '0/1')
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    if int(den) > 0:
                        metadata['fps'] = round(float(num) / float(den), 2)
                metadata['pix_fmt'] = stream.get('pix_fmt', '')
                metadata['profile'] = stream.get('profile', '')
            elif stream.get('codec_type') == 'audio':
                metadata['has_audio'] = True
                metadata['audio_codec'] = stream.get('codec_name', '')
                metadata['audio_channels'] = stream.get('channels', 0)
                metadata['audio_sample_rate'] = int(stream.get('sample_rate', 0))

    except FileNotFoundError:
        metadata['error'] = '未找到 ffprobe，请安装 FFmpeg'
    except subprocess.TimeoutExpired:
        metadata['error'] = 'ffprobe 执行超时'
    except Exception as e:
        metadata['error'] = str(e)

    return metadata


def positive_interval(value):
    interval = float(value)
    if isinstance(value, bool) or not math.isfinite(interval) or interval <= 0:
        raise ValueError('抽帧间隔必须为有限正数')
    return interval


def extract_video_frames(file_path: str, output_dir: str, interval: float = 3.0) -> list:
    """从视频中按间隔提取关键帧"""
    interval = positive_interval(interval)
    os.makedirs(output_dir, exist_ok=True)
    frames = []

    try:
        metadata = get_video_metadata(file_path)
        duration = metadata.get('duration_seconds', 0)
        if duration <= 0:
            return frames

        t = 0
        while t < duration:
            frame_path = os.path.join(output_dir, 'frame_%04d_%.1fs.jpg' % (len(frames), t))
            cmd = [
                'ffmpeg', '-y', '-ss', str(t), '-i', file_path,
                '-vframes', '1', '-q:v', '2', frame_path
            ]
            subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.exists(frame_path):
                frames.append({'index': len(frames), 'timestamp': t, 'path': frame_path})
            t += interval

    except FileNotFoundError:
        print("[WARNING] 未找到 ffmpeg，无法提取视频帧", file=sys.stderr)
    except Exception as e:
        print("[WARNING] 帧提取失败: %s" % e, file=sys.stderr)

    return frames


def extract_video_audio(file_path: str, output_dir: str = None) -> dict:
    """从视频中提取音频为 WAV（16kHz 单声道，供语音识别）"""
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    audio_path = os.path.join(output_dir, Path(file_path).stem + '_audio.wav')

    try:
        cmd = [
            'ffmpeg', '-i', file_path, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1', '-y', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and os.path.exists(audio_path):
            return {'success': True, 'audio_path': audio_path, 'size_bytes': os.path.getsize(audio_path)}
        return {'success': False, 'error': '音频提取失败: ' + result.stderr[:500]}
    except FileNotFoundError:
        return {'success': False, 'error': 'ffmpeg 未安装'}
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': '音频提取超时（文件可能较大）'}
    except Exception as e:
        return {'success': False, 'error': '音频提取出错: ' + str(e)}


def parse_script_structure(text: str) -> dict:
    """识别剧本结构：场次、角色、对白、场景描述"""
    structure = {
        'scenes': [],
        'characters': set(),
        'total_lines': len(text.split('\n')),
    }

    lines = text.split('\n')
    current_scene = None
    scene_patterns = ['第', '场', 'Scene', 'SCENE', 'scene', '幕', '景', '日', '夜', '内', '外']

    for line in lines:
        line = line.strip()
        if not line:
            continue

        is_scene_marker = False
        for pattern in scene_patterns:
            if pattern in line and len(line) < 60:
                is_scene_marker = True
                break

        if is_scene_marker:
            if current_scene:
                structure['scenes'].append(current_scene)
            current_scene = {'marker': line, 'content': []}
        elif current_scene is not None:
            current_scene['content'].append(line)

        if '：' in line or ':' in line:
            parts = line.replace(':', '：').split('：', 1)
            if len(parts) == 2 and len(parts[0]) <= 6:
                structure['characters'].add(parts[0].strip())

    if current_scene:
        structure['scenes'].append(current_scene)

    structure['characters'] = list(structure['characters'])
    return structure


def main():
    parser = argparse.ArgumentParser(description='多格式文件解析工具')
    parser.add_argument('file_path', help='输入文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--type', '-t', choices=['pdf', 'txt', 'docx', 'video', 'auto'],
                        default='auto', help='文件类型（默认自动检测）')
    parser.add_argument('--video-frames', help='视频帧输出目录')
    parser.add_argument('--frame-interval', type=positive_interval, default=3.0,
                        help='视频帧提取间隔（秒，默认3秒）')
    parser.add_argument('--extract-audio', action='store_true',
                        help='从视频提取 16kHz 单声道 WAV 供语音识别')
    parser.add_argument('--structure', action='store_true',
                        help='尝试解析剧本结构')

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print('错误：文件不存在 - ' + args.file_path, file=sys.stderr)
        sys.exit(1)

    if args.type == 'auto':
        ext = os.path.splitext(args.file_path)[1].lower()
        type_map = {
            '.pdf': 'pdf', '.txt': 'txt', '.docx': 'docx', '.doc': 'docx',
            '.mp4': 'video', '.mov': 'video', '.avi': 'video', '.mkv': 'video', '.webm': 'video',
        }
        file_type = type_map.get(ext, 'txt')
    else:
        file_type = args.type

    result = {}

    if file_type == 'video':
        metadata = get_video_metadata(args.file_path)
        result = {'type': 'video', 'metadata': metadata}

        if args.video_frames:
            result['frames'] = extract_video_frames(args.file_path, args.video_frames, args.frame_interval)
        if args.extract_audio:
            result['audio_extraction'] = extract_video_audio(args.file_path)
    else:
        parsers = {'pdf': parse_pdf, 'docx': parse_docx, 'txt': parse_txt}
        text = parsers.get(file_type, parse_txt)(args.file_path)
        result = {'type': 'text', 'file_type': file_type, 'text': text}

        if args.structure and text:
            result['structure'] = parse_script_structure(text)

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print('结果已写入: ' + args.output)
    else:
        print(output)


if __name__ == '__main__':
    main()
