$(document).ready(function () {
          $('#id_hisobot').change(function () {
              const hisobotId = $(this).val();
              $.ajax({
                  url: "{% url 'ajax_load_hisobot_davri' %}",
                  data: {
                      'hisobot': hisobotId
                  },
                  success: function (data) {
                      const $hisobotDavri = $('#id_hisobot_davri');
                      $hisobotDavri.empty();
                      $hisobotDavri.append('<option value="">Hisobot davrini tanlang</option>');
                      data.forEach(function (item) {
                          $hisobotDavri.append(`<option value="${item.id}">${item.name}</option>`);
                      });
                  }
              });
          });
      });