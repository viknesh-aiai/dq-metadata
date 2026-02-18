from sqlalchemy import Column, String, Boolean, Integer, PrimaryKeyConstraint
from app.db.base import Base


class MetadataColumn(Base):
    """
    Mapping for the external 'metadata_columns' table.
    This table is treated as read-only.
    """
    __tablename__ = "metadata_columns"

    # The table might not have a single primary key in the source.
    # We define a composite primary key for SQLAlchemy mapping purposes.
    # Adjust based on real schema if known. 
    # For now, (table_schema, table_name, column_name) implies uniqueness.
    
    app_name = Column(String, nullable=False)
    table_schema = Column(String, primary_key=True)
    table_name = Column(String, primary_key=True)
    column_name = Column(String, primary_key=True)
    data_type = Column(String, nullable=False)
    is_nullable = Column(Boolean, default=True)

    def __repr__(self):
        return f"<MetadataColumn(schema={self.table_schema}, table={self.table_name}, name={self.column_name})>"
