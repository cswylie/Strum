export interface Message {
  message: string;
  history: {question: string, answer: string}[];
}

export interface ResponseMessage {
    history: {question: string, answer: string}[];
    response: string;
}