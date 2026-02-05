package com.example.controller;

import com.example.service.ChatService;
import dev.langchain4j.model.openai.OpenAiChatModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

@RestController
public class ChatController {
    @Autowired
    private OpenAiChatModel model;
    @Autowired
    private ChatService chatService;

    @RequestMapping(value = "/chat", produces = "text/html;charset=UTF-8")
    public Flux<String> chat(@RequestParam("memoryId")String memoryId, @RequestParam("message")String message){
        Flux<String> res = chatService.chat(memoryId, message);
        return res;
    }
}
