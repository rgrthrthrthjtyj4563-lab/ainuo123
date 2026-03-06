package com.ainuo.wordstructure.service;

import com.ainuo.wordstructure.domain.model.StructureNode;

import java.util.List;

public class ExtractionPayload {
    private String fileName;
    private String fileHash;
    private List<StructureNode> structure;

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getFileHash() {
        return fileHash;
    }

    public void setFileHash(String fileHash) {
        this.fileHash = fileHash;
    }

    public List<StructureNode> getStructure() {
        return structure;
    }

    public void setStructure(List<StructureNode> structure) {
        this.structure = structure;
    }
}
