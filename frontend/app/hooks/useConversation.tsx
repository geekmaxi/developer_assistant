import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { getCookie, setCookie } from "../utils/cookies";
import { TOKEN_COOKIE_NAME, apiBaseUrl } from "../utils/constants";

export function useConversation() {
    const [conversationIds, setConversationIds] = useState<number[]>([]);

    useEffect(() => {
        
    })
}