"use client";

import { v4 as uuidv4 } from "uuid";
import { ChatWindow } from "./components/ChatWindow";
import { ToastContainer } from "react-toastify";
import { Conversation } from "./components/Conversation";

import { ChakraProvider } from "@chakra-ui/react";
// import { useUser } from "./hooks/useUser";
import { useEffect, useState } from "react";
import usePersistentState from './hooks/usePersistentState';

export default function Home() {
  // const {token} = useUser();

  const [conversationId, setConversationId] = usePersistentState<string>("conversation-id", uuidv4())  
  return (
    <ChakraProvider>
      <ToastContainer />
      {/* <div className="flex f-row h-full"> */}
        {/* <Conversation></Conversation> */}
        <ChatWindow conversationId={conversationId}></ChatWindow>
      {/* </div> */}

    </ChakraProvider>
  );
}

