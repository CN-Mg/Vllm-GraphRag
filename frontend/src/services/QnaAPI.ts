import axios from 'axios';
import { url } from '../utils/Utils';
import { UserCredentials } from '../types';

export interface ImageNode {
  img_url: string;
  file_name: string;
  page_number: number;
  img_index: number;
  chunks: Array<{
    chunk_id: string;
    chunk_text: string;
  }>;
}

export const chatBotAPI = async (
  userCredentials: UserCredentials | undefined,
  question: string,
  session_id: string,
  model: string,
  mode: string,
  document_names?: (string | undefined)[],
  image_url?: string
) => {
  try {
    const formData = new FormData();
    formData.append('uri', userCredentials?.uri ?? '');
    formData.append('database', userCredentials?.database ?? '');
    formData.append('userName', userCredentials?.userName ?? '');
    formData.append('password', userCredentials?.password ?? '');
    formData.append('question', question);
    formData.append('session_id', session_id);
    formData.append('model', model);
    formData.append('mode', mode);
    if (document_names) {
      formData.append('document_names', JSON.stringify(document_names));
    }
    if (image_url) {
      formData.append('image_url', image_url);
    }
    const startTime = Date.now();
    const response = await axios.post(`${url()}/chat_bot`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    const endTime = Date.now();
    const timeTaken = endTime - startTime;
    return { response: response, timeTaken: timeTaken };
  } catch (error) {
    console.log('Error Posting the Question:', error);
    throw error;
  }
};

export const getImagesListAPI = async (
  userCredentials: UserCredentials | undefined,
  document_names?: (string | undefined)[]
) => {
  try {
    const formData = new FormData();
    formData.append('uri', userCredentials?.uri ?? '');
    formData.append('database', userCredentials?.database ?? '');
    formData.append('userName', userCredentials?.userName ?? '');
    formData.append('password', userCredentials?.password ?? '');
    if (document_names) {
      formData.append('document_names', JSON.stringify(document_names));
    }
    const startTime = Date.now();
    const response = await axios.post(`${url()}/images_list`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    const endTime = Date.now();
    const timeTaken = endTime - startTime;
    return { response: response, timeTaken: timeTaken };
  } catch (error) {
    console.log('Error Getting Images List:', error);
    throw error;
  }
};

export const clearChatAPI = async (userCredentials: UserCredentials, session_id: string) => {
  try {
    const formData = new FormData();
    formData.append('uri', userCredentials?.uri ?? '');
    formData.append('database', userCredentials?.database ?? '');
    formData.append('userName', userCredentials?.userName ?? '');
    formData.append('password', userCredentials?.password ?? '');
    formData.append('session_id', session_id);
    const response = await axios.post(`${url()}/clear_chat_bot`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  } catch (error) {
    console.log('Error Posting the Question:', error);
    throw error;
  }
};
