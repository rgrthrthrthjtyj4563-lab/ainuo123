package com.ainuo.wordstructure.api;

import com.ainuo.wordstructure.application.WordStructureApplicationService;
import com.ainuo.wordstructure.domain.model.ExtractionResult;
import com.ainuo.wordstructure.domain.model.StructureNode;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = WordStructureController.class)
public class WordStructureControllerTest {
    @Autowired
    private MockMvc mockMvc;
    @MockBean
    private WordStructureApplicationService applicationService;

    @Test
    void shouldReturnExtractResult() throws Exception {
        ExtractionResult result = new ExtractionResult();
        result.setExtractionId(101L);
        StructureNode node = new StructureNode();
        node.setTitle("1 总体");
        node.setLevel(1);
        result.setStructure(List.of(node));
        Mockito.when(applicationService.extract(Mockito.any(), Mockito.anyString())).thenReturn(result);
        MockMultipartFile file = new MockMultipartFile("file", "demo.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", new byte[]{1, 2, 3});
        mockMvc.perform(multipart("/api/v1/structures/extract").file(file))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.extractionId").value(101))
                .andExpect(jsonPath("$.data.structure[0].title").value("1 总体"));
    }
}
