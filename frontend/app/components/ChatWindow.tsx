"use client";

import React, { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { RemoteRunnable } from "@langchain/core/runnables/remote";
import { applyPatch } from "@langchain/core/utils/json_patch";

import { EmptyState } from "./EmptyState";
import { ChatMessageBubble, Message } from "./ChatMessageBubble";
import { AutoResizeTextarea } from "./AutoResizeTextarea";
import { marked } from "marked";
import { Renderer } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/gradient-dark.css";

import "react-toastify/dist/ReactToastify.css";
import {
  Heading,
  Flex,
  IconButton,
  InputGroup,
  InputRightElement,
  Spinner,
} from "@chakra-ui/react";
import { ArrowUpIcon } from "@chakra-ui/icons";
import { Select, Link } from "@chakra-ui/react";
import { Source } from "./SourceBubble";
import { apiBaseUrl } from "../utils/constants";
// import { useMessageHistory } from "../hooks/userMessageHistory"
// import useLocalStorageState from "../hooks/userMessageHistory";
import usePersistentState from "../hooks/usePersistentState";

const MODEL_TYPES = [
  "deepseek_v3",
  "llama2_chinese",
  "openai_gpt_3_5_turbo",
  "qwen_max"
  // "anthropic_claude_3_haiku",
  // "google_gemini_pro",
  // "fireworks_mixtral",
  // "cohere_command",
];

const defaultLlmValue =
  MODEL_TYPES[Math.floor(Math.random() * MODEL_TYPES.length)];


export function ChatWindow(props: { conversationId: string }) {

  const conversationId = props.conversationId;

  const searchParams = useSearchParams();

  const messageContainerRef = useRef<HTMLDivElement | null>(null);
  // const [messages, setMessages] = useState<Array<Message>>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [llm, setLlm] = useState(
    searchParams.get("llm") ?? "openai_gpt_3_5_turbo",
  );

  const [messages, setMessages] = usePersistentState<Array<Message>>(
    "message-" + conversationId,
    [],
  );
  console.log(messages)

  const [llmIsLoading, setLlmIsLoading] = useState(true);
  useEffect(() => {
    setLlm(searchParams.get("llm") ?? defaultLlmValue);
    setLlmIsLoading(false);
  }, [searchParams]);

  // const [chatHistory, setChatHistory] = useState<
  //   { human: string; ai: string }[]
  // >([]);

  const sendMessage = async (message?: string) => {
    if (messageContainerRef.current) {
      messageContainerRef.current.classList.add("grow");
    }
    if (isLoading) {
      return;
    }
    const messageValue = message ?? input;
    if (messageValue === "") return;
    setInput("");
    setMessages((prevMessages) => [
      ...prevMessages,
      { id: Math.random().toString(), content: messageValue, role: "user" },
    ]);
    setIsLoading(true);

    let accumulatedMessage = "";
    let runId: string | undefined = undefined;
    let sources: Source[] | undefined = undefined;
    let messageIndex: number | null = null;

    let renderer = new Renderer();
    renderer.paragraph = (text) => {
      return text + "\n";
    };
    renderer.list = (text) => {
      return `${text}\n\n`;
    };
    renderer.listitem = (text) => {
      return `\n• ${text}`;
    };
    renderer.code = (code, language) => {
      const validLanguage = hljs.getLanguage(language || "")
        ? language
        : "plaintext";
      const highlightedCode = hljs.highlight(
        validLanguage || "plaintext",
        code,
      ).value;
      return `<pre class="highlight bg-gray-700" style="padding: 5px; border-radius: 5px; overflow: auto; overflow-wrap: anywhere; white-space: pre-wrap; max-width: 100%; display: block; line-height: 1.2"><code class="${language}" style="color: #d6e2ef; font-size: 12px; ">${highlightedCode}</code></pre>`;
    };
    marked.setOptions({ renderer });
    try {
      const sourceStepName = "FindDocs";
      let streamedResponse: Record<string, any> = {};
      const remoteChain = new RemoteRunnable({
        url: apiBaseUrl + "/api",
        options: {
          timeout: 60000,
        },
      });
      const llmDisplayName = llm ?? "openai_gpt_3_5_turbo";
      const streamLog = await remoteChain.streamLog(
        {
          question: messageValue,
          chat_history: [],//chatHistory,
        },
        {
          configurable: {
            llm: llmDisplayName,
            session_id: conversationId,
          },
          tags: ["model:" + llmDisplayName],
          metadata: {
            llm: llmDisplayName,
          },
        },
        {
          includeNames: [sourceStepName],
        },
      );
      for await (const chunk of streamLog) {
        streamedResponse = applyPatch(streamedResponse, chunk.ops, undefined, false).newDocument;
        if (
          Array.isArray(
            streamedResponse?.logs?.[sourceStepName]?.final_output?.output?.docs,
          )
        ) {
          sources = streamedResponse.logs[
            sourceStepName
          ].final_output.output.docs.map((doc: Record<string, any>) => ({
            url: doc.metadata.source,
            title: doc.metadata.title,
          }));
        }
        if (streamedResponse.id !== undefined) {
          runId = streamedResponse.id;
        }
        if (Array.isArray(streamedResponse?.streamed_output)) {
          accumulatedMessage = streamedResponse.streamed_output.join("");
        }
        const parsedResult = marked.parse(accumulatedMessage);

        setMessages((prevMessages) => {
          let newMessages = [...prevMessages];
          if (
            messageIndex === null ||
            newMessages[messageIndex] === undefined
          ) {
            messageIndex = newMessages.length;
            newMessages.push({
              id: Math.random().toString(),
              content: parsedResult.trim(),
              runId: runId,
              sources: sources,
              role: "assistant",
            });
          } else if (newMessages[messageIndex] !== undefined) {
            newMessages[messageIndex].content = parsedResult.trim();
            newMessages[messageIndex].runId = runId;
            newMessages[messageIndex].sources = sources;
          }
          return newMessages;
        });
        // setMessageHistory((prevMessages) => [
        //   ...prevMessages,
        //   ...messages.slice(-1)
        // ]);
      }
      // setChatHistory((prevChatHistory) => [
      //   ...prevChatHistory,
      //   { human: messageValue, ai: accumulatedMessage },
      // ]);
      setIsLoading(false);
    } catch (e) {
      // messageContainerRef.current.classList.remove("grow")
      // setMessages((prevMessages) => prevMessages.slice(0, -1));
      // setMessages
      setIsLoading(false);
      setInput(messageValue);
      throw e;
    }
  };

  const sendInitialQuestion = async (question: string) => {
    await sendMessage(question);
  };

  const insertUrlParam = (key: string, value?: string) => {
    if (window.history.pushState) {
      const searchParams = new URLSearchParams(window.location.search);
      searchParams.set(key, value ?? "");
      const newurl =
        window.location.protocol +
        "//" +
        window.location.host +
        window.location.pathname +
        "?" +
        searchParams.toString();
      window.history.pushState({ path: newurl }, "", newurl);
    }
  };

  return (
    <div className="flex flex-col items-center p-8 rounded grow max-h-full pt-0 pb-0">
      <Flex
        direction={messages.length > 0 ? "row" : "column"}
        alignItems={messages.length > 0 ? "top" : "center"}
        justifyContent={"space-between"}
        width={"100%"}
        marginTop={messages.length > 0 ? "" : "64px"}
        marginBottom={messages.length > 0 ? "8px" : ""}

      >
        <Heading
          fontSize={messages.length > 0 ? "4xl" : "3xl"}
          fontWeight={"medium"}
          mb={1}
          color={"white"}
          className={"flex items-center"}
        >
          <svg width="32" height="32" className="icon mr-2" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7352" id="mx_n_1739939042343" ><path d="M837.12 656.896V366.592c0-25.6-14.848-49.664-36.864-64.512l-251.904-144.896c-22.016-12.8-51.2-12.8-73.728 0l-250.88 145.408c-22.016 12.8-36.864 36.864-36.864 64.512v291.84c0 25.6 14.848 49.664 36.864 64.512l251.904 143.36c22.016 12.8 51.2 12.8 73.728 0l251.904-144.896c23.04-13.312 35.84-37.376 35.84-65.024z" fill="#ffffff" opacity=".2" p-id="7353"></path><path d="M611.84 668.16h-84.992l-27.648-82.944H367.104l-27.648 82.944H254.464l132.096-363.52h90.624l134.656 363.52z m-128-144.384l-41.472-126.464c-2.048-7.68-4.096-17.92-6.144-31.744h-2.048c0 9.728-4.096 21.504-6.144 31.744l-41.472 126.464h97.28z m252.416-221.184v363.52h-76.8v-363.52h76.8z" fill="#ffffff" p-id="7354"></path><path d="M945.664 612.864c-14.848 0-27.648 12.8-27.648 27.648v77.312c0 16.384-9.216 31.232-24.064 40.448l-354.304 203.776c-14.848 9.216-33.28 9.216-47.616 0l-354.304-203.776c-14.848-7.168-24.064-24.064-24.064-40.448v-102.4c26.112-11.776 44.032-37.888 44.032-68.608 0-41.472-33.792-75.264-75.264-75.264S6.656 505.344 6.656 546.816c0 33.28 21.504 61.44 51.2 71.168v99.328c0 36.864 19.968 69.632 51.2 88.064l354.304 205.824c16.384 9.216 33.28 12.8 51.2 12.8 16.384 0 34.816-5.632 51.2-14.848l352.768-203.776c31.232-18.432 51.2-51.2 51.2-88.064V640c1.536-15.872-9.728-27.136-24.064-27.136zM973.312 395.776V306.176c0-36.864-19.968-69.632-51.2-88.064L567.296 14.336c-31.232-18.432-71.68-18.432-102.912 0L109.568 218.112c-31.232 18.432-51.2 51.2-51.2 88.064v69.632c0 14.848 12.8 27.648 27.648 27.648 14.848 0 27.648-12.8 27.648-27.648V306.176c0-16.384 9.216-31.232 24.064-40.448l354.304-203.776c14.848-9.216 33.28-9.216 47.616 0l352.768 205.824c14.848 7.168 24.064 24.064 24.064 40.448v85.504c-28.672 10.752-49.664 37.888-49.664 70.656 0 41.472 33.792 75.264 75.264 75.264s75.264-33.792 75.264-75.264c0-30.72-18.432-56.832-44.032-68.608z" fill="#ffffff" p-id="7355"></path></svg>
          Deveploment Assistant
        </Heading>
        {/* {messages.length > 0 ? (
          <Heading fontSize="md" fontWeight={"normal"} mb={1} color={"white"}>
            We appreciate feedback!
          </Heading>
        ) : (
          <Heading
            fontSize="xl"
            fontWeight={"normal"}
            color={"white"}
            marginTop={"10px"}
            textAlign={"center"}
          >
            Ask me any questions about development work.
          </Heading>
        )} */}
        <div className="text-white flex flex-wrap items-center">
          <div className="flex items-center mb-2">
            <span className="shrink-0 mr-2">Powered by</span>
            {llmIsLoading ? (
              <Spinner className="my-2"></Spinner>
            ) : (
              <Select
                value={llm}
                onChange={(e) => {
                  insertUrlParam("llm", e.target.value);
                  setLlm(e.target.value);
                }}
                width={"240px"}
              >
        
                <option value="openai_gpt_3_5_turbo">GPT-3.5-Turbo</option>
                <option value="deepseek_v3">DeepSeek V3</option>
                <option value="llama2_chinese">LLAMA2 Chineses</option>
                <option value="qwen_max">通义千问-Max</option>
              </Select>
            )}
          </div>
        </div>
      </Flex>
      <div
        className="flex flex-col-reverse w-full mb-2 overflow-auto bg-stone-900 pl-6 pt-4"
        ref={messageContainerRef}
      >
        {messages.length > 0 ? (
          [...messages]
            .reverse()
            .map((m, index) => (
              <ChatMessageBubble
                key={m.id}
                message={{ ...m }}
                aiEmoji="🦜"
                isMostRecent={index === 0}
                messageCompleted={!isLoading}
              ></ChatMessageBubble>
            ))
        ) : (
          <EmptyState onChoice={sendInitialQuestion} />
        )}
      </div>
      <InputGroup size="md" alignItems={"center"} className="mb-2 mt-2" >
        <AutoResizeTextarea
          value={input}
          maxRows={5}
          marginRight={"56px"}
          placeholder="问一问"
          textColor={"white"}
          borderColor={"rgb(58, 58, 61)"}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            } else if (e.key === "Enter" && e.shiftKey) {
              e.preventDefault();
              setInput(input + "\n");
            }
          }}
        />
        <InputRightElement h="full">
          <IconButton
            colorScheme="blue"
            rounded={"full"}
            aria-label="Send"
            icon={isLoading ? <Spinner /> : <ArrowUpIcon />}
            type="submit"
            onClick={(e) => {
              e.preventDefault();
              sendMessage();
            }}
          />
        </InputRightElement>
      </InputGroup>

      {messages.length === 0 ? (
        <footer className="flex justify-center absolute bottom-8">
          <a
            href="https://github.com/geekmaxi/development_assistant"
            target="_blank"
            className="text-white flex items-center"
          >
            <img src="/images/github-mark.svg" className="h-4 mr-1" />
            <span>View Source</span>
          </a>
        </footer>
      ) : (
        ""
      )}
    </div>
  );
}
