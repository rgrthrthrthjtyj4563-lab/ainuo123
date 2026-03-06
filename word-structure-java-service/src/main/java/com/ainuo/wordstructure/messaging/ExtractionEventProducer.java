package com.ainuo.wordstructure.messaging;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.rocketmq.client.producer.SendCallback;
import org.apache.rocketmq.client.producer.SendResult;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.stereotype.Component;
import org.apache.rocketmq.spring.core.RocketMQTemplate;

import java.util.HashMap;
import java.util.Map;

@Component
public class ExtractionEventProducer {
    private final RocketMQTemplate rocketMQTemplate;
    private final ObjectMapper objectMapper;
    @Value("${word.rules.mq-topic}")
    private String topic;

    public ExtractionEventProducer(RocketMQTemplate rocketMQTemplate, ObjectMapper objectMapper) {
        this.rocketMQTemplate = rocketMQTemplate;
        this.objectMapper = objectMapper;
    }

    public void sendExtractionEvent(Long extractionId, String fileHash, Integer nodeCount) {
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("extractionId", extractionId);
            payload.put("fileHash", fileHash);
            payload.put("nodeCount", nodeCount);
            payload.put("eventType", "WORD_STRUCTURE_EXTRACTED");
            String body = objectMapper.writeValueAsString(payload);
            rocketMQTemplate.asyncSend(
                    topic,
                    MessageBuilder.withPayload(body).build(),
                    new SendCallback() {
                        @Override
                        public void onSuccess(SendResult sendResult) {
                        }

                        @Override
                        public void onException(Throwable throwable) {
                        }
                    }
            );
        } catch (Exception ignored) {
        }
    }
}
