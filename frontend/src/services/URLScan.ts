import axios from 'axios';
import { url } from '../utils/Utils';
import { ScanProps, ServerResponse } from '../types';

/* URLScan.ts 定义了与 URL 扫描相关的 API 调用函数，主要用于处理用户输入的 URL（如网页链接等），并将其发送到后端进行扫描和处理 */
const urlScanAPI = async (props: ScanProps) => {
  try {
    const formData = new FormData();
    formData.append('uri', props?.userCredentials?.uri ?? '');
    formData.append('database', props?.userCredentials?.database ?? '');
    formData.append('userName', props?.userCredentials?.userName ?? '');
    formData.append('password', props?.userCredentials?.password ?? '');
    formData.append('source_url', props?.urlParam ?? '');
    formData.append('source_type', props?.source_type ?? '');
    if (props.model != undefined) {
      formData.append('model', props?.model);
    }

    const response: ServerResponse = await axios.post(`${url()}/url/scan`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  } catch (error) {
    console.log('Error uploading file:', error);
    throw error;
  }
};

export { urlScanAPI };
