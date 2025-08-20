import axios from 'axios';
import { response } from 'express';

import { Message, ResponseMessage } from './strum.index';

export class StrumService {
  public async sendMessage(body: Message): Promise<ResponseMessage> {
    const { message, history } = body;
    // console.log(`Sending message: ${message}`);
    // console.log(history);

    // Gonna be a chain of backend calls
    try {
      const ragResponse = await axios.post('http://rag_service:8000/query', {
        message: message,
        history: history ?? [],
      });

      return {
        response: ragResponse.data.response,
        history: ragResponse.data.history,
      };
    } catch (error) {
      console.error('Failed to call RAG API:', error);
      throw new Error('RAG service error');
    }
  }
}
