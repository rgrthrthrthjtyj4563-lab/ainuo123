package com.ainuo.wordstructure.service;

public class RuleClassifyResult {
    private final String nodeType;
    private final double confidence;
    private final String reason;

    public RuleClassifyResult(String nodeType, double confidence, String reason) {
        this.nodeType = nodeType;
        this.confidence = confidence;
        this.reason = reason;
    }

    public String getNodeType() {
        return nodeType;
    }

    public double getConfidence() {
        return confidence;
    }

    public String getReason() {
        return reason;
    }
}
