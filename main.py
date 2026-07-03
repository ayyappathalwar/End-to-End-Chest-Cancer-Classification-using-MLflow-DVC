from dotenv import load_dotenv
load_dotenv(override=True)

from cnnClassifier import logger
from cnnClassifier.pipeline.stage_01_data_ingestion import DataIngestionTrainingPipeline
from cnnClassifier.pipeline.stage_02_prepare_base_model import PrepareBaseModelTrainingPipeline
from cnnClassifier.pipeline.stage_03_model_trainer import ModelTrainerPipeline
from cnnClassifier.pipeline.stage_04_model_evaluation import EvaluationPipeline 



STAGE_NAME = "Data Ingestion stage"


try:
    logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
    obj = DataIngestionTrainingPipeline()
    obj.main()
    logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<<\n\nx==========x")
except Exception as e:
    logger.exception(e)
    raise e


STAGE_NAME = "Prepare base model"
try:
        logger.info(f"****************")
        logger.info(f">>>>>>> stage {STAGE_NAME} started >>>>>>")
        obj = PrepareBaseModelTrainingPipeline()
        obj.main()
        logger.info(f">>>>>>> stage {STAGE_NAME} completed >>>>>>")

except Exception as e:
    logger.exception(e)
    raise e



STAGE_NAME = "Training"
try:
        logger.info(f"****************")
        logger.info(f">>>>>>> stage {STAGE_NAME} started >>>>>>")
        model_trainer = ModelTrainerPipeline()
        model_trainer.main()
        logger.info(f">>>>>>> stage {STAGE_NAME} completed >>>>>>")
except Exception as e:
    logger.exception(e)
    raise e



STAGE_NAME = "Evaluation Stage"
try:
        logger.info(f"****************")
        logger.info(f">>>>>>> stage {STAGE_NAME} started >>>>>>")
        model_eval = EvaluationPipeline()
        model_eval.main()
        logger.info(f">>>>>>> stage {STAGE_NAME} completed >>>>>>")
except Exception as e:
    logger.exception(e)
    raise e