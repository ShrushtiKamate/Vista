
def calculate_compliance_score(
    document_score,
    infrastructure_score,
    anomaly_score,
    additional_score=0
):
    """
    Calculate the overall compliance score.

    Parameters:
        document_score (float): Document verification score out of 100.
        infrastructure_score (float): Infrastructure inspection score out of 100.
        anomaly_score (float): Data consistency score out of 100.
        additional_score (float): Additional inspection score out of 100.

    Returns:
        float: Overall compliance score.
    """

    weights = {
        "documents": 0.30,
        "infrastructure": 0.40,
        "anomaly": 0.20,
        "additional": 0.10
    }

    final_score = (
        document_score * weights["documents"]
        + infrastructure_score * weights["infrastructure"]
        + anomaly_score * weights["anomaly"]
        + additional_score * weights["additional"]
    )

    return round(final_score, 2)


def get_compliance_status(score):
    """
    Convert the numerical score into a compliance category.
    """

    if score >= 80:
        return "Compliant"
    elif score >= 60:
        return "Partially Compliant"
    else:
        return "Non-Compliant"


if __name__ == "__main__":

    # Sample inspection results
    document_score = 85
    infrastructure_score = 90
    anomaly_score = 80
    additional_score = 70

    score = calculate_compliance_score(
        document_score,
        infrastructure_score,
        anomaly_score,
        additional_score
    )

    status = get_compliance_status(score)

    print("VISTA Institutional Inspection")
    print("--------------------------------")
    print(f"Document Score       : {document_score}/100")
    print(f"Infrastructure Score : {infrastructure_score}/100")
    print(f"Anomaly Score        : {anomaly_score}/100")
    print(f"Additional Score     : {additional_score}/100")
    print("--------------------------------")
    print(f"Final Score          : {score}/100")
    print(f"Compliance Status    : {status}")