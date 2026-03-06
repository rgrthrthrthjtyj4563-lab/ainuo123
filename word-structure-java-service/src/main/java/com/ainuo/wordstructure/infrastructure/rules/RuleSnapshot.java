package com.ainuo.wordstructure.infrastructure.rules;

public class RuleSnapshot {
    private String signature;
    private RuleDefinition definition;

    public RuleSnapshot() {
    }

    public RuleSnapshot(String signature, RuleDefinition definition) {
        this.signature = signature;
        this.definition = definition;
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }

    public RuleDefinition getDefinition() {
        return definition;
    }

    public void setDefinition(RuleDefinition definition) {
        this.definition = definition;
    }
}
