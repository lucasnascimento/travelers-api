import csv
import os
import tempfile

from flask import Blueprint, after_this_request, send_file
from flask_jwt_extended import jwt_required
from sqlalchemy import text

from database import db

admin_report_bp = Blueprint("admin_report", __name__)


@admin_report_bp.route(
    "/report/finnancial", defaults={"itinerary_id": None}, methods=["GET"]
)
@admin_report_bp.route("/report/finnancial/<itinerary_id>", methods=["GET"])
@jwt_required()
def get_finnancial_report(itinerary_id):
    query = text(
        """
         with finnancial_report as (
         select coalesce(ii.due_date::date, i.inserted_at::Date) as "Data",
         	   coalesce(ii.amount_cents::decimal, i.total_cents::decimal)/100 as "Montante",
         	   bt.traveler_name as "Memo",
         	   ins."name" || ' - ' || it.title as "De",
         	   ins."name" as "Categoria",
         	   it.title as "Subcategoria",
         	   i."method",
         	   (select count(*) from booking_traveler bt where bt.booking_id = b.id) as "QtdeViajantes",
         	   coalesce(ii.installment::text, '1') as installment,
         	   coalesce(i.invoice_extras->>'installments', '1') as "installments",
         	   i.invoice_id,
         	   b.payer_name as "PagadorNome",
         	   b.payer_email  as "PagadorEmail",
         	   b.payer_phone  as "PagadorFone"
           from invoice i
           left join booking b
             on i.booking_id = b.id
           left join booking_traveler bt
             on bt.booking_id = b.id
           left join itinerary it
             on it.id = b.itinerary_id
          left join institution ins
             on ins.id = it.institution_id
           left join invoice_installment ii
             on ii.invoice_id = i.id
          where i.status = 'PAID'
            and (:itinerary_id is NULL or it.id = :itinerary_id)
          order by bt.traveler_name, installment
         )
         select distinct "Data",
                replace(to_char("Montante"/"QtdeViajantes", '999999.99'),'.',',') "Montante",
                initcap("Memo") as "Memo",
                "De",
                "Categoria",
                "Subcategoria",
                "method",
                installment || ' de ' || "installments" as "Parcela",
                "PagadorNome",
                "PagadorEmail",
                "PagadorFone"
         from finnancial_report order by "Memo" asc
        """
    )
    results = db.session.execute(query, {"itinerary_id": itinerary_id})
    rows = results.fetchall()
    column_names = results.keys()

    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, suffix=".csv", newline=""
    ) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(zip(column_names, row)))
        temp_path = csvfile.name

    @after_this_request
    def remove_file(response):
        os.remove(temp_path)
        return response

    return send_file(
        temp_path, as_attachment=True, download_name="finnancial_report.csv"
    )


@admin_report_bp.route(
    "/report/travelers", defaults={"itinerary_id": None}, methods=["GET"]
)
@admin_report_bp.route("/report/travelers/<itinerary_id>", methods=["GET"])
@jwt_required()
def get_travelers_report(itinerary_id):
    query = text(
        """
         with travelers_report as (
         select initcap(bt.traveler_name) as "Nome completo do viajante",
                bt.traveler_extras->'documents'->>'cpf' as "CPF",
                bt.traveler_extras->'documents'->>'rg' as "RG",
                bt.traveler_extras->>'document-date' as "RG emissão",
                bt.traveler_extras->>'document-issuer' as "RG emissor",
                bt.traveler_extras->'documents'->>'rne' as "RNE",
                coalesce(bt.traveler_extras->>'passport',bt.traveler_extras->>'passaport') as "Passaporte",
                coalesce(bt.traveler_extras->>'passport_country',bt.traveler_extras->>'passaport_country') as "Passaporte País",
                bt.traveler_extras->>'room-grade' as "Unidade",
                bt.traveler_birthdate as "Data nascimento",
                case
                	when bt.traveler_gender = 'Male' then 'Masculino'
                	when bt.traveler_gender = 'Female' then 'Feminino'
                	when bt.traveler_gender = 'Other' then 'Outro'
                end as "Gênero do viajante",
                bt.inserted_at::date as "Data da reserva",
                initcap(b.payer_name) as "Nome do responsável",
                b.payer_email as "Email do responsável",
                b.payer_phone as "Telefone do responsável",
                inst.name as "Nome da instituição",
                it.title as "Nome do roteiro"
           from booking_traveler bt
          inner join booking b on bt.booking_id = b.id
          inner join itinerary it on it.id = b.itinerary_id
          inner join institution inst on inst.id = it.institution_id
          inner join invoice i on i.booking_id = b.id
          where i.status = 'PAID'
            and (:itinerary_id is NULL or it.id = :itinerary_id)
         )
         select * from travelers_report order by "Nome do roteiro", "Nome completo do viajante";
        """
    )
    results = db.session.execute(query, {"itinerary_id": itinerary_id})
    rows = results.fetchall()
    column_names = results.keys()

    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, suffix=".csv", newline=""
    ) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_names)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(zip(column_names, row)))
        temp_path = csvfile.name

    @after_this_request
    def remove_file(response):
        os.remove(temp_path)
        return response

    return send_file(
        temp_path, as_attachment=True, download_name="travelers_report.csv"
    )
