* --- ЗАГРУЗКА ОСНОВНЫХ ДАННЫХ ---
use "1-kb/2021/perv", clear

* --- ОБЪЕДИНЕНИЕ С КАТАЛОГОМ ---
merge m:1 okpo inn using "1-kb/2021/katalog.dta", keep(match) keepusing(soato soogu oked skfs opf ptp) nogenerate

* --- ПРОВЕРКА И ПЕРЕИМЕНОВАНИЕ ---
ds razdel ns
if "`r(varlist)'" != "" {
    rename (razdel ns) (bob satr)
}

* --- ОЧИСТКА ДАННЫХ ---
keep okpo inn bob satr g* soato soogu oked skfs ptp opf
duplicates drop
duplicates drop okpo bob satr inn soato soogu oked skfs ptp opf, force

* --- СОЗДАНИЕ НОВЫХ ПЕРЕМЕННЫХ ---
gen soato7 = substr(soato, 1, 7)
gen soato4 = substr(soato, 1, 4)
drop soato

* --- СОХРАНЕНИЕ ВРЕМЕННОГО ФАЙЛА ---
save temp, replace

* --- РАЗДЕЛЕНИЕ ПО ГРАФАМ ---
use temp, clear
ds, has(type string)
local tasnif `r(varlist)'
ds g*
local grafa `r(varlist)'

* --- СОЗДАНИЕ ОТДЕЛЬНЫХ ФАЙЛОВ ДЛЯ КАЖДОЙ ГРАФЫ ---
foreach gr in `grafa' {
    use temp, clear
    keep `tasnif' `gr'
    rename `gr' g
    gen ustun = substr("`gr'", 2, .)
    drop if missing(g) | g == 0
    save "temp/`gr'", replace
}

* --- ОБЪЕДИНЕНИЕ ДАННЫХ ---
use "temp/g1", clear
di "`grafa'"

foreach gr in `grafa' {
    if "`gr'" == "g1" {
        continue
    }
    append using "temp/`gr'"
}

* --- СОХРАНЕНИЕ СВОДНЫХ ДАННЫХ ---
save svodga, replace

* --- АГРЕГИРОВАНИЕ ДАННЫХ ---
collapse (sum) g, by(bob satr soogu oked skfs ptp opf soato7 soato4 ustun)

save svodga1, replace

* --- СОЗДАНИЕ ФАЙЛОВ ДЛЯ КАЖДОГО РАЗРЕЗА ---
use svodga1, clear
ds, has(type string)

foreach kesim in `r(varlist)' {
    if !inlist("`kesim'", "bob", "satr", "ustun") {
        use svodga1, clear
        keep bob satr ustun g `kesim'
        rename `kesim' kesim
        gen kesim_turi = "`kesim'"
        collapse (sum) g, by(kesim_turi bob satr ustun kesim)
        save "temp/`kesim'", replace
    }
}
