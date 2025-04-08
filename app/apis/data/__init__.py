from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, UploadFile, File, Form
from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Create router
router = APIRouter(prefix="/data", tags=["data"])

# Define paths for storing data
DATA_DIR = Path("data/datasets")
DATA_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/datasets")
async def list_datasets():
    """List all available datasets"""
    datasets = []
    for dataset_file in DATA_DIR.glob("*.csv"):
        datasets.append({
            "id": dataset_file.stem,
            "name": dataset_file.stem,
            "type": "csv",
            "size": dataset_file.stat().st_size,
            "last_modified": dataset_file.stat().st_mtime
        })
    
    for dataset_file in DATA_DIR.glob("*.json"):
        datasets.append({
            "id": dataset_file.stem,
            "name": dataset_file.stem,
            "type": "json",
            "size": dataset_file.stat().st_size,
            "last_modified": dataset_file.stat().st_mtime
        })
    
    return {"datasets": datasets}

@router.get("/datasets/{dataset_id}")
async def get_dataset_info(dataset_id: str):
    """Get information about a specific dataset"""
    # Check for CSV file
    csv_path = DATA_DIR / f"{dataset_id}.csv"
    if csv_path.exists():
        # Read the first few rows to get column info
        df = pd.read_csv(csv_path, nrows=5)
        return {
            "id": dataset_id,
            "name": dataset_id,
            "type": "csv",
            "size": csv_path.stat().st_size,
            "last_modified": csv_path.stat().st_mtime,
            "columns": df.columns.tolist(),
            "sample": df.head().to_dict(orient="records")
        }
    
    # Check for JSON file
    json_path = DATA_DIR / f"{dataset_id}.json"
    if json_path.exists():
        with open(json_path, "r") as f:
            data = json.load(f)
        
        # If it's a list of records, return sample
        if isinstance(data, list) and len(data) > 0:
            sample = data[:5] if len(data) >= 5 else data
            return {
                "id": dataset_id,
                "name": dataset_id,
                "type": "json",
                "size": json_path.stat().st_size,
                "last_modified": json_path.stat().st_mtime,
                "record_count": len(data),
                "sample": sample
            }
        else:
            return {
                "id": dataset_id,
                "name": dataset_id,
                "type": "json",
                "size": json_path.stat().st_size,
                "last_modified": json_path.stat().st_mtime,
                "data": data
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Dataset {dataset_id} not found"
    )

@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None)
):
    """Upload a new dataset"""
    # Get file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in [".csv", ".json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and JSON files are supported"
        )
    
    # Use provided name or original filename without extension
    if dataset_name:
        dataset_id = dataset_name
    else:
        dataset_id = os.path.splitext(file.filename)[0]
    
    # Save the file
    file_path = DATA_DIR / f"{dataset_id}{file_ext}"
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {
        "id": dataset_id,
        "name": dataset_id,
        "type": file_ext[1:],  # Remove the dot
        "size": file_path.stat().st_size,
        "message": "Dataset uploaded successfully"
    }

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset"""
    # Check for CSV file
    csv_path = DATA_DIR / f"{dataset_id}.csv"
    if csv_path.exists():
        csv_path.unlink()
        return {"id": dataset_id, "message": "Dataset deleted successfully"}
    
    # Check for JSON file
    json_path = DATA_DIR / f"{dataset_id}.json"
    if json_path.exists():
        json_path.unlink()
        return {"id": dataset_id, "message": "Dataset deleted successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Dataset {dataset_id} not found"
    )

@router.post("/datasets/{dataset_id}/analyze")
async def analyze_dataset(dataset_id: str, analysis_type: str):
    """Analyze a dataset"""
    # Check for CSV file
    csv_path = DATA_DIR / f"{dataset_id}.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        
        if analysis_type == "summary":
            # Basic summary statistics
            summary = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
                "missing_values": df.isnull().sum().to_dict()
            }
            return summary
        
        elif analysis_type == "statistics":
            # Detailed statistics for numeric columns
            stats = {}
            for col in df.select_dtypes(include=["number"]).columns:
                stats[col] = {
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "unique_count": df[col].nunique()
                }
            return stats
        
        elif analysis_type == "categorical":
            # Analysis of categorical columns
            categorical = {}
            for col in df.select_dtypes(include=["object"]).columns:
                value_counts = df[col].value_counts().to_dict()
                categorical[col] = {
                    "unique_count": df[col].nunique(),
                    "top_values": dict(list(value_counts.items())[:10]),
                    "missing_count": df[col].isnull().sum()
                }
            return categorical
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis type {analysis_type} not supported"
            )
    
    # Check for JSON file
    json_path = DATA_DIR / f"{dataset_id}.json"
    if json_path.exists():
        with open(json_path, "r") as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # Convert to DataFrame for analysis
            df = pd.DataFrame(data)
            
            if analysis_type == "summary":
                # Basic summary statistics
                summary = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": df.columns.tolist(),
                    "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
                    "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
                    "missing_values": df.isnull().sum().to_dict()
                }
                return summary
            
            elif analysis_type == "statistics":
                # Detailed statistics for numeric columns
                stats = {}
                for col in df.select_dtypes(include=["number"]).columns:
                    stats[col] = {
                        "min": df[col].min(),
                        "max": df[col].max(),
                        "mean": df[col].mean(),
                        "median": df[col].median(),
                        "std": df[col].std(),
                        "unique_count": df[col].nunique()
                    }
                return stats
            
            elif analysis_type == "categorical":
                # Analysis of categorical columns
                categorical = {}
                for col in df.select_dtypes(include=["object"]).columns:
                    value_counts = df[col].value_counts().to_dict()
                    categorical[col] = {
                        "unique_count": df[col].nunique(),
                        "top_values": dict(list(value_counts.items())[:10]),
                        "missing_count": df[col].isnull().sum()
                    }
                return categorical
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Analysis type {analysis_type} not supported"
                )
        else:
            # For non-tabular JSON, just return basic info
            return {
                "type": "json",
                "structure": "object",
                "keys": list(data.keys()) if isinstance(data, dict) else None
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Dataset {dataset_id} not found"
    )
