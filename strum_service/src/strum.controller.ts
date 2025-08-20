import {
  Body,
  Controller,
  Post,
  Get,
  Response,
  Route,
  SuccessResponse,
  Request,
} from 'tsoa';
import express from 'express';


import { StrumService } from './strum.service';
import { Message, ResponseMessage } from './strum.index';



@Route('sendMessage')
export class createMessageController extends Controller {
  @Post()
  @Response('500', 'Unable to Query Chatbot')
  @SuccessResponse('200', 'Message Sent')
  public async sendMessage(
    @Body() body: Message,
    @Request() request: express.Request // superfluous, only for handling meta-data like headers, cookies
  ): Promise<ResponseMessage | undefined> {
    return new StrumService()
      .sendMessage(body)
      .then(
        async (result: ResponseMessage): Promise<ResponseMessage | undefined> => {
          // Make sure to have add more error handling for bad requests and such
          if (!result) {
            this.setStatus(500);
          }
          return {
            history: result.history,
            response: result.response,
          };
        }
      );
  }
}