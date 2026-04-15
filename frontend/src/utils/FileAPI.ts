import { Method } from 'axios';
import { url } from './Utils';
import { UserCredentials, ExtractParams, UploadParams } from '../types';
import { apiCall } from '../services/CommonAPI';

// Upload Call
export const uploadAPI = async (
  file: Blob,
  userCredentials: UserCredentials,
  model: string,
  chunkNumber: number,
  totalChunks: number,
  originalname: string
): Promise<any> => {
  const urlUpload = `${url()}/upload`;
  const method: Method = 'post';
  const commonParams: UserCredentials = userCredentials;
  const additionalParams: UploadParams = { file, model, chunkNumber, totalChunks, originalname };
  const response = await apiCall(urlUpload, method, commonParams, additionalParams);
  return response;
};

// Extract call
export const extractAPI = async (
  model: string,
  userCredentials: UserCredentials,
  source_type: string,
  source_url?: string,
  file_name?: string,
  allowedNodes?: string[],
  allowedRelationship?: string[]
): Promise<any> => {
  const urlExtract = `${url()}/extract`;
  const method: Method = 'post';
  const commonParams: UserCredentials = userCredentials;
  let additionalParams: ExtractParams;
  if (source_type === 'web-url') {
    additionalParams = {
      model,
      source_url,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
    };
  } else {
    additionalParams = {
      model,
      source_type,
      file_name,
      allowedNodes,
      allowedRelationship,
    };
  }
  const response = await apiCall(urlExtract, method, commonParams, additionalParams);
  return response;
};
