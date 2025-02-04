# Copyright (c) Alibaba, Inc. and its affiliates.

import os
from typing import Any, Dict, List, Union

from modelscope.metainfo import Preprocessors
from modelscope.models.base import Model
from modelscope.utils.constant import Fields, Frameworks
from .base import Preprocessor
from .builder import PREPROCESSORS

__all__ = ['WavToScp']


@PREPROCESSORS.register_module(
    Fields.audio, module_name=Preprocessors.wav_to_scp)
class WavToScp(Preprocessor):
    """generate audio scp from wave or ark
    """

    def __init__(self):
        pass

    def __call__(self,
                 model: Model = None,
                 recog_type: str = None,
                 audio_format: str = None,
                 audio_in: Union[str, bytes] = None,
                 audio_fs: int = None) -> Dict[str, Any]:
        assert model is not None, 'preprocess model is empty'
        assert recog_type is not None and len(
            recog_type) > 0, 'preprocess recog_type is empty'
        assert audio_format is not None, 'preprocess audio_format is empty'
        assert audio_in is not None, 'preprocess audio_in is empty'

        self.am_model = model
        out = self.forward(self.am_model.forward(), recog_type, audio_format,
                           audio_in, audio_fs)
        return out

    def forward(self, model: Dict[str,
                                  Any], recog_type: str, audio_format: str,
                audio_in: Union[str, bytes], audio_fs: int) -> Dict[str, Any]:
        assert len(recog_type) > 0, 'preprocess recog_type is empty'
        assert len(audio_format) > 0, 'preprocess audio_format is empty'
        assert len(
            model['am_model']) > 0, 'preprocess model[am_model] is empty'
        assert len(model['am_model_path']
                   ) > 0, 'preprocess model[am_model_path] is empty'
        assert os.path.exists(
            model['am_model_path']), 'preprocess am_model_path does not exist'
        assert len(model['model_workspace']
                   ) > 0, 'preprocess model[model_workspace] is empty'
        assert os.path.exists(model['model_workspace']
                              ), 'preprocess model_workspace does not exist'
        assert len(model['model_config']
                   ) > 0, 'preprocess model[model_config] is empty'

        rst = {
            # the recognition model dir path
            'model_workspace': model['model_workspace'],
            # the am model name
            'am_model': model['am_model'],
            # the am model file path
            'am_model_path': model['am_model_path'],
            # the asr type setting, eg: test dev train wav
            'recog_type': recog_type,
            # the asr audio format setting, eg: wav, pcm, kaldi_ark, tfrecord
            'audio_format': audio_format,
            # the recognition model config dict
            'model_config': model['model_config'],
            # the sample rate of audio_in
            'audio_fs': audio_fs
        }

        if isinstance(audio_in, str):
            # wav file path or the dataset path
            rst['wav_path'] = audio_in

        out = self.config_checking(rst)
        out = self.env_setting(out)
        if audio_format == 'wav':
            out['audio_lists'] = self.scp_generation_from_wav(out)
        elif audio_format == 'kaldi_ark':
            out['audio_lists'] = self.scp_generation_from_ark(out)
        elif audio_format == 'tfrecord':
            out['audio_lists'] = os.path.join(out['wav_path'], 'data.records')
        elif audio_format == 'pcm':
            out['audio_lists'] = audio_in

        return out

    def config_checking(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """config checking
        """

        assert inputs['model_config'].__contains__(
            'type'), 'model type does not exist'
        inputs['model_type'] = inputs['model_config']['type']

        if inputs['model_type'] == Frameworks.torch:
            assert inputs['model_config'].__contains__(
                'batch_size'), 'batch_size does not exist'
            assert inputs['model_config'].__contains__(
                'am_model_config'), 'am_model_config does not exist'
            assert inputs['model_config'].__contains__(
                'asr_model_config'), 'asr_model_config does not exist'
            assert inputs['model_config'].__contains__(
                'asr_model_wav_config'), 'asr_model_wav_config does not exist'

            am_model_config: str = os.path.join(
                inputs['model_workspace'],
                inputs['model_config']['am_model_config'])
            assert os.path.exists(
                am_model_config), 'am_model_config does not exist'
            inputs['am_model_config'] = am_model_config

            asr_model_config: str = os.path.join(
                inputs['model_workspace'],
                inputs['model_config']['asr_model_config'])
            assert os.path.exists(
                asr_model_config), 'asr_model_config does not exist'

            asr_model_wav_config: str = os.path.join(
                inputs['model_workspace'],
                inputs['model_config']['asr_model_wav_config'])
            assert os.path.exists(
                asr_model_wav_config), 'asr_model_wav_config does not exist'

            if inputs['audio_format'] == 'wav' or inputs[
                    'audio_format'] == 'pcm':
                inputs['asr_model_config'] = asr_model_wav_config
            else:
                inputs['asr_model_config'] = asr_model_config

            if inputs['model_config'].__contains__('mvn_file'):
                mvn_file = os.path.join(inputs['model_workspace'],
                                        inputs['model_config']['mvn_file'])
                assert os.path.exists(mvn_file), 'mvn_file does not exist'
                inputs['mvn_file'] = mvn_file

        elif inputs['model_type'] == Frameworks.tf:
            assert inputs['model_config'].__contains__(
                'vocab_file'), 'vocab_file does not exist'
            vocab_file: str = os.path.join(
                inputs['model_workspace'],
                inputs['model_config']['vocab_file'])
            assert os.path.exists(vocab_file), 'vocab file does not exist'
            inputs['vocab_file'] = vocab_file

            assert inputs['model_config'].__contains__(
                'am_mvn_file'), 'am_mvn_file does not exist'
            am_mvn_file: str = os.path.join(
                inputs['model_workspace'],
                inputs['model_config']['am_mvn_file'])
            assert os.path.exists(am_mvn_file), 'am mvn file does not exist'
            inputs['am_mvn_file'] = am_mvn_file

        else:
            raise ValueError('model type is mismatched')

        return inputs

    def env_setting(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # run with datasets, should set datasets_path and text_path
        if inputs['recog_type'] != 'wav':
            inputs['datasets_path'] = inputs['wav_path']

            # run with datasets, and audio format is waveform
            if inputs['audio_format'] == 'wav':
                inputs['wav_path'] = os.path.join(inputs['datasets_path'],
                                                  'wav', inputs['recog_type'])
                inputs['reference_text'] = os.path.join(
                    inputs['datasets_path'], 'transcript', 'data.text')
                assert os.path.exists(
                    inputs['reference_text']), 'reference text does not exist'

            # run with datasets, and audio format is kaldi_ark
            elif inputs['audio_format'] == 'kaldi_ark':
                inputs['wav_path'] = os.path.join(inputs['datasets_path'],
                                                  inputs['recog_type'])
                inputs['reference_text'] = os.path.join(
                    inputs['wav_path'], 'data.text')
                assert os.path.exists(
                    inputs['reference_text']), 'reference text does not exist'

            # run with datasets, and audio format is tfrecord
            elif inputs['audio_format'] == 'tfrecord':
                inputs['wav_path'] = os.path.join(inputs['datasets_path'],
                                                  inputs['recog_type'])
                inputs['reference_text'] = os.path.join(
                    inputs['wav_path'], 'data.txt')
                assert os.path.exists(
                    inputs['reference_text']), 'reference text does not exist'
                inputs['idx_text'] = os.path.join(inputs['wav_path'],
                                                  'data.idx')
                assert os.path.exists(
                    inputs['idx_text']), 'idx text does not exist'

        # set asr model language
        if 'lang' in inputs['model_config']:
            inputs['model_lang'] = inputs['model_config']['lang']
        else:
            inputs['model_lang'] = 'zh-cn'

        return inputs

    def scp_generation_from_wav(self, inputs: Dict[str, Any]) -> List[Any]:
        """scp generation from waveform files
        """
        from easyasr.common import asr_utils

        # find all waveform files
        wav_list = []
        if inputs['recog_type'] == 'wav':
            file_path = inputs['wav_path']
            if os.path.isfile(file_path):
                if file_path.endswith('.wav') or file_path.endswith('.WAV'):
                    wav_list.append(file_path)
        else:
            wav_dir: str = inputs['wav_path']
            wav_list = asr_utils.recursion_dir_all_wav(wav_list, wav_dir)

        list_count: int = len(wav_list)
        inputs['wav_count'] = list_count

        # store all wav into audio list
        audio_lists = []
        j: int = 0
        while j < list_count:
            wav_file = wav_list[j]
            wave_key: str = os.path.splitext(os.path.basename(wav_file))[0]
            item = {'key': wave_key, 'file': wav_file}
            audio_lists.append(item)
            j += 1

        return audio_lists

    def scp_generation_from_ark(self, inputs: Dict[str, Any]) -> List[Any]:
        """scp generation from kaldi ark file
        """

        ark_scp_path = os.path.join(inputs['wav_path'], 'data.scp')
        ark_file_path = os.path.join(inputs['wav_path'], 'data.ark')
        assert os.path.exists(ark_scp_path), 'data.scp does not exist'
        assert os.path.exists(ark_file_path), 'data.ark does not exist'

        with open(ark_scp_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # store all ark item into audio list
        audio_lists = []
        for line in lines:
            outs = line.strip().split(' ')
            if len(outs) == 2:
                key = outs[0]
                sub = outs[1].split(':')
                if len(sub) == 2:
                    nums = sub[1]
                    content = ark_file_path + ':' + nums
                    item = {'key': key, 'file': content}
                    audio_lists.append(item)

        return audio_lists
