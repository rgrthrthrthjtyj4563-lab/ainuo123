from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.database import ReportStructure, StructureNode
from app.schemas.report_structure import (
    ReportStructureCreate, ReportStructureUpdate,
    StructureNodeUpdate
)

class StructureService:
    def __init__(self, db: Session):
        self.db = db

    def get_structures(self, skip: int = 0, limit: int = 20, is_active: bool = None) -> tuple[List[ReportStructure], int]:
        query = select(ReportStructure)
        if is_active is not None:
            query = query.where(ReportStructure.is_active == is_active)
        
        # Calculate total count
        count_query = select(func.count()).select_from(query.subquery())
        # For SQLite/MySQL compatibility in simple count
        # Alternatively:
        total = self.db.query(ReportStructure).filter(
            ReportStructure.is_active == is_active if is_active is not None else True
        ).count()
        
        structures = self.db.execute(query.order_by(ReportStructure.created_at.desc()).offset(skip).limit(limit)).scalars().all()
        return structures, total

    def get_structure(self, structure_id: int) -> Optional[ReportStructure]:
        return self.db.get(ReportStructure, structure_id)

    def create_structure(self, structure_data: ReportStructureCreate) -> ReportStructure:
        structure = ReportStructure(**structure_data.model_dump())
        self.db.add(structure)
        self.db.commit()
        self.db.refresh(structure)
        return structure

    def update_structure(self, structure_id: int, structure_data: ReportStructureUpdate) -> Optional[ReportStructure]:
        structure = self.get_structure(structure_id)
        if not structure:
            return None
        
        for key, value in structure_data.model_dump(exclude_unset=True).items():
            setattr(structure, key, value)
            
        self.db.commit()
        self.db.refresh(structure)
        return structure

    def delete_structure(self, structure_id: int) -> bool:
        structure = self.get_structure(structure_id)
        if not structure:
            return False
        self.db.delete(structure)
        self.db.commit()
        return True

    def get_structure_nodes(self, structure_id: int) -> List[StructureNode]:
        # Fetch all nodes for the structure
        nodes = self.db.execute(
            select(StructureNode)
            .where(StructureNode.structure_id == structure_id)
            .order_by(StructureNode.level, StructureNode.sort_order)
        ).scalars().all()
        
        return self._build_tree(nodes)

    def _build_tree(self, nodes: List[StructureNode]) -> List[StructureNode]:
        # This function reconstructs the tree from a flat list of nodes
        # Note: We are modifying the objects in memory to populate 'children'
        
        # Create a map for O(1) access
        node_map = {node.id: node for node in nodes}
        root_nodes = []
        
        from sqlalchemy.orm.attributes import set_committed_value

        # Initialize children lists to empty for all nodes to prevent lazy loading queries
        # and to ensure we build the tree from the fetched nodes only.
        for node in nodes:
            # Force set children to empty list to avoid DB queries and start fresh
            set_committed_value(node, 'children', [])

        for node in nodes:
            if node.parent_id is None:
                root_nodes.append(node)
            else:
                parent = node_map.get(node.parent_id)
                if parent:
                    parent.children.append(node)
        
        # Sort children
        for node in nodes:
            if node.children:
                node.children.sort(key=lambda x: x.sort_order)
                 
        return sorted(root_nodes, key=lambda x: x.sort_order)

    def update_node(self, node_id: int, node_data: StructureNodeUpdate) -> Optional[StructureNode]:
        node = self.db.get(StructureNode, node_id)
        if not node:
            return None
        
        for key, value in node_data.model_dump(exclude_unset=True).items():
            setattr(node, key, value)
            
        self.db.commit()
        self.db.refresh(node)
        return node

    def delete_node(self, node_id: int) -> bool:
        node = self.db.get(StructureNode, node_id)
        if not node:
            return False
        self.db.delete(node)
        self.db.commit()
        return True
