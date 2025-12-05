from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ml.model_loader import predict_disease


class DiseasePredictionAPI(APIView):
    """
    API endpoint to predict livestock disease.
    """

    def post(self, request):
        try:
            data = request.data

            # Extract input fields
            animal = data.get("animal")              # e.g., "cow"
            age = float(data.get("age"))             # e.g., 3
            temperature = float(data.get("temperature"))  # e.g., 103.1
            symptoms = data.get("symptoms", [])      # list of strings

            # Validate input
            if not animal or not symptoms:
                return Response(
                    {"error": "Animal type and at least one symptom are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Predict disease
            result = predict_disease(animal, age, temperature, symptoms)

            return Response({"predicted_disease": result})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
